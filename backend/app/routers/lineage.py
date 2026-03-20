"""
Lineage metadata endpoints.
Returns pipeline lineage graph (source → bronze → silver) and column-level PII provenance.
Attempts to enrich with live Unity Catalog metadata when Databricks is configured.
Falls back to schema-derived placeholders otherwise.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from databricks.sdk import WorkspaceClient

from backend.app.models import (
    TableLineage, LineageNode, LineageEdge, ColumnLineage,
    LineageNodeType, SUPPORTED_DOMAINS,
)
from backend.app.config import Settings, get_settings
from backend.app.connectors import get_databricks_optional

router = APIRouter()

# PII column metadata per domain — mirrors databricks/src/mask.py PII_FIELDS
_PII_FIELDS: dict[str, list[str]] = {
    "customer": ["first_name", "last_name", "email", "phone", "ssn", "address"],
    "order":    ["customer_id", "billing_address", "shipping_address"],
    "loyalty":  ["customer_id", "email"],
}

# Schema columns per domain (post-transform Silver column names)
_SILVER_COLUMNS: dict[str, list[str]] = {
    "customer": ["customer_id", "given_name", "family_name", "email", "phone", "ssn",
                 "address", "created_date", "email_domain",
                 "_tdm_pipeline_run_id", "_tdm_source_layer", "_tdm_masking_applied", "_tdm_ingested_at"],
    "order":    ["order_id", "customer_id", "order_date", "total_amount", "status",
                 "billing_address", "shipping_address",
                 "_tdm_pipeline_run_id", "_tdm_source_layer", "_tdm_masking_applied", "_tdm_ingested_at"],
    "product":  ["product_id", "name", "category", "price", "in_stock", "name_upper",
                 "_tdm_pipeline_run_id", "_tdm_source_layer", "_tdm_masking_applied", "_tdm_ingested_at"],
    "inventory":["inventory_id", "product_id", "location_id", "quantity", "updated_at",
                 "_tdm_pipeline_run_id", "_tdm_source_layer", "_tdm_masking_applied", "_tdm_ingested_at"],
    "loyalty":  ["loyalty_id", "customer_id", "email", "points", "tier", "enrolled_date",
                 "_tdm_pipeline_run_id", "_tdm_source_layer", "_tdm_masking_applied", "_tdm_ingested_at"],
}

# Map Silver column names back to Bronze source column names (rename tracking)
_RENAME_MAP: dict[str, dict[str, str]] = {
    "customer": {"given_name": "first_name", "family_name": "last_name"},
}


def _build_lineage(
    domain: str,
    catalog: str,
    schema: str,
    pipeline_run_id: Optional[str],
    settings: Settings,
) -> TableLineage:
    s3_source = f"s3://{settings.tdm_s3_bucket}/raw/{domain}/"
    pii_fields = _PII_FIELDS.get(domain, [])
    renames    = _RENAME_MAP.get(domain, {})

    nodes = [
        LineageNode(
            id=f"s3-{domain}",
            name=s3_source,
            type=LineageNodeType.S3,
            location=s3_source,
        ),
        LineageNode(
            id=f"bronze-{domain}",
            name=f"bronze_{domain}",
            type=LineageNodeType.BRONZE,
            catalog=catalog,
            schema_name=schema,
            location=f"{catalog}.{schema}.bronze_{domain}",
        ),
        LineageNode(
            id=f"silver-{domain}",
            name=f"silver_{domain}",
            type=LineageNodeType.SILVER,
            catalog=catalog,
            schema_name=schema,
            location=f"{catalog}.{schema}.silver_{domain}",
        ),
    ]

    edges = [
        LineageEdge(from_node=f"s3-{domain}",     to_node=f"bronze-{domain}", transform="ingest"),
        LineageEdge(from_node=f"bronze-{domain}",  to_node=f"silver-{domain}", transform="mask+transform"),
    ]

    columns = []
    for col in _SILVER_COLUMNS.get(domain, []):
        source_col = renames.get(col, col)
        is_pii     = source_col in pii_fields
        is_masked  = is_pii
        columns.append(ColumnLineage(
            column=col,
            pii=is_pii,
            masked=is_masked,
            masking_strategy="hash" if is_masked else None,
            source_column=source_col,
        ))

    return TableLineage(
        table=f"silver_{domain}",
        domain=domain,
        nodes=nodes,
        edges=edges,
        columns=columns,
        pipeline_run_id=pipeline_run_id,
    )


def _try_enrich_from_unity_catalog(
    lineage: TableLineage,
    db: WorkspaceClient,
    catalog: str,
    schema: str,
    domain: str,
) -> TableLineage:
    """Attempt to read actual column metadata from Unity Catalog.
    Silently returns the original lineage if the table doesn't exist or UC is unavailable.
    """
    try:
        table = db.tables.get(f"{catalog}.{schema}.silver_{domain}")
        if table.columns:
            lineage.columns = [
                ColumnLineage(
                    column=c.name,
                    pii="pii" in (c.type_json or "").lower()
                        or c.name in _PII_FIELDS.get(domain, []),
                    masked=c.name in _PII_FIELDS.get(domain, []),
                    masking_strategy="hash" if c.name in _PII_FIELDS.get(domain, []) else None,
                    source_column=_RENAME_MAP.get(domain, {}).get(c.name, c.name),
                )
                for c in table.columns
            ]
    except Exception:
        pass  # UC not available — use schema-derived placeholders
    return lineage


@router.get("/{domain}", response_model=TableLineage)
def get_domain_lineage(
    domain: str,
    catalog: str = "tdm_catalog",
    schema: str = "tdm_dev",
    pipeline_run_id: str = None,
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
    settings: Settings = Depends(get_settings),
):
    """Get pipeline lineage graph for a domain (S3 → Bronze → Silver).
    Column-level PII provenance is always returned.
    Enriched with live Unity Catalog metadata when Databricks is configured.
    """
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found.")

    lineage = _build_lineage(domain, catalog, schema, pipeline_run_id, settings)

    if db:
        lineage = _try_enrich_from_unity_catalog(lineage, db, catalog, schema, domain)

    return lineage


@router.get("/{domain}/{table}", response_model=TableLineage)
def get_table_lineage(
    domain: str,
    table: str,
    catalog: str = "tdm_catalog",
    schema: str = "tdm_dev",
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
    settings: Settings = Depends(get_settings),
):
    """Get lineage for a specific table within a domain (e.g. bronze_customer, silver_order)."""
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found.")

    lineage = _build_lineage(domain, catalog, schema, None, settings)

    # Filter to just the requested table's perspective
    lineage.table = table
    if db:
        lineage = _try_enrich_from_unity_catalog(lineage, db, catalog, schema, domain)

    return lineage
