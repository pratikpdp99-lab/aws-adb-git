"""
Unity Catalog registration and tagging.
Registers Delta tables with descriptions and column-level PII tags.
All operations are best-effort — failures are logged, not raised,
so the pipeline does not break when running outside a UC-enabled workspace.
"""

from pyspark.sql import SparkSession
from databricks.src.mask import PII_FIELDS


TABLE_DESCRIPTIONS = {
    "bronze_customer": "Raw customer records ingested from S3. Restrict access — contains unmasked PII.",
    "silver_customer": "Masked and standardised customer records. Safe for lower environments.",
    "bronze_order":    "Raw order records from S3.",
    "silver_order":    "Masked order records with standardised types.",
    "bronze_product":  "Raw product catalog from S3.",
    "silver_product":  "Standardised product catalog.",
    "dq_results":      "Data quality check results for all TDM pipeline runs.",
}


def _safe(fn):
    """Run fn, print warning on failure instead of raising."""
    try:
        fn()
    except Exception as e:
        print(f"[catalog] Warning: {e}")


def register_table(
    spark: SparkSession,
    catalog: str,
    schema: str,
    table: str,
    description: str,
) -> None:
    full = f"{catalog}.{schema}.{table}"
    _safe(lambda: spark.sql(f"COMMENT ON TABLE {full} IS '{description}'"))
    print(f"[catalog] Registered: {full}")


def tag_pii_columns(
    spark: SparkSession,
    catalog: str,
    schema: str,
    domain: str,
) -> None:
    """Apply Unity Catalog column-level PII tags on silver tables."""
    full = f"{catalog}.{schema}.silver_{domain}"
    for col in PII_FIELDS.get(domain, []):
        _safe(lambda c=col: spark.sql(
            f"ALTER TABLE {full} ALTER COLUMN {c} "
            f"SET TAGS ('pii' = 'true', 'masked' = 'true', 'tdm_tokenized' = 'true')"
        ))


def ensure_schema(spark: SparkSession, catalog: str, schema: str) -> None:
    """Create catalog and schema if they don't exist."""
    _safe(lambda: spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}"))
    _safe(lambda: spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}"))


def register_all(spark: SparkSession, catalog: str, schema: str) -> None:
    """Register all TDM tables with descriptions and PII column tags."""
    ensure_schema(spark, catalog, schema)
    for table, desc in TABLE_DESCRIPTIONS.items():
        register_table(spark, catalog, schema, table, desc)
    for domain in ["customer", "order", "product"]:
        tag_pii_columns(spark, catalog, schema, domain)
