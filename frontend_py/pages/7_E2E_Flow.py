"""E2E Flow — one-page pipeline architecture explainer."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from lib.auth import require_login

st.set_page_config(page_title="E2E Flow | TDM", layout="wide")
require_login()

st.title("🔄 End-to-End Pipeline Flow")
st.caption("How raw retail data becomes masked, validated test data in lower environments.")

# ── Pipeline diagram ───────────────────────────────────────────────────────────
st.subheader("Architecture Diagram")
st.markdown("""
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TDM PIPELINE — Deckers Brands                        │
└─────────────────────────────────────────────────────────────────────────────┘

  S3 (raw CSV/Parquet)
        │
        │  ingest.py: read CSV → Bronze Delta
        ▼
  ┌──────────────┐
  │  BRONZE      │  raw retail data, schema-on-read
  │  bronze_*    │  columns: as-is from source
  └──────────────┘
        │
        │  quality.py: CompletenessCheck, UniquenessCheck, ValidityCheck
        ▼
  ┌──────────────┐
  │  DQ CHECKS   │  per-domain rule registry (DQ_RULES)
  │              │  → dq_results Delta table (audit trail)
  │              │  → pipeline blocked if checks fail
  └──────────────┘
        │
        │  mask.py: SHA-256 hash PII fields (deterministic tokenisation)
        ▼
  ┌──────────────┐
  │  MASKING     │  PII_FIELDS per domain hashed/redacted
  │              │  strategy: hash | redact | nullify | partial
  └──────────────┘
        │
        │  transform.py: domain-specific standardisation + lineage columns
        ▼
  ┌──────────────┐
  │  SILVER      │  masked + standardised + _tdm_* lineage columns
  │  silver_*    │  customer: given_name, family_name, email_domain
  └──────────────┘
        │
        │  catalog.py: register in Unity Catalog
        ▼
  ┌──────────────┐
  │  UNITY       │  tdm_catalog.tdm_dev.silver_customer etc.
  │  CATALOG     │  column-level lineage, PII tags, row-count
  └──────────────┘
        │
        │  FastAPI: /datasets/, /domains/, /jobs/
        ▼
  ┌──────────────┐
  │  API         │  Pydantic models, auth, request workflow
  │  Backend     │  compliance_tags on DomainField responses
  └──────────────┘
        │
        ▼
  Next.js / Streamlit Frontend
```
""")

# ── Tabbed walkthrough ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Stage Walkthrough")

t_ingest, t_mask, t_dq, t_transform, t_catalog, t_api = st.tabs([
    "1 · Ingest", "2 · Mask", "3 · DQ Checks", "4 · Transform", "5 · Catalog", "6 · API",
])

with t_ingest:
    st.markdown("### Ingest: S3 → Bronze Delta")
    st.markdown("""
    **File:** `databricks/src/ingest.py`

    Reads raw CSV/Parquet files from S3 into Bronze Delta tables.
    No transformations — data is stored as-is for reprocessability.
    """)
    st.code("""
# ingest.py
def ingest(spark, s3_path, domain, catalog, schema, run_id):
    df = spark.read.option("header", True).csv(s3_path)
    df = df.withColumn("_tdm_run_id", F.lit(run_id))
    table = table_name(catalog, schema, f"bronze_{domain}")
    df.write.format("delta").mode("overwrite").saveAsTable(table)
    """, language="python")

with t_mask:
    st.markdown("### Mask: SHA-256 Tokenisation")
    st.markdown("""
    **File:** `databricks/src/mask.py`

    All PII fields are replaced with deterministic SHA-256 hashes.
    This preserves join stability across environments (same input → same hash).
    """)
    st.code("""
# mask.py
PII_FIELDS = {
    "customer": ["email", "phone", "ssn", "first_name", "last_name", "address"],
    "order":    ["customer_id", "billing_address", "shipping_address"],
    "payment":  ["customer_id", "card_last4"],
}

def hash_column(df, col_name):
    hash_udf = F.udf(lambda v: hashlib.sha256(v.encode()).hexdigest() if v else None)
    return df.withColumn(col_name, hash_udf(F.col(col_name)))
    """, language="python")

with t_dq:
    st.markdown("### Data Quality Checks")
    st.markdown("""
    **File:** `databricks/src/quality.py`

    Three check types run against every domain before Silver write:
    - **CompletenessCheck** — null rate ≤ threshold
    - **UniquenessCheck** — no duplicates in key column
    - **ValidityCheck** — regex pattern match rate ≥ threshold

    Results are written to `dq_results` Delta table. Pipeline stops if any check fails.
    """)
    st.code("""
# quality.py
DQ_RULES = {
    "customer": [
        CompletenessCheck("customer_id"),
        CompletenessCheck("email"),
        UniquenessCheck("customer_id"),
        ValidityCheck("email", r"^[^@]+@[^@]+\\.[^@]+$"),
    ],
    "payment": [
        CompletenessCheck("payment_id"),
        UniquenessCheck("payment_id"),
        ValidityCheck("status", r"^(CAPTURED|REFUNDED|DECLINED|PENDING)$"),
    ],
}
    """, language="python")

with t_transform:
    st.markdown("### Transform: Bronze → Silver")
    st.markdown("""
    **File:** `databricks/src/transform.py`

    Domain-specific standardisation + TDM lineage metadata columns:
    - `_tdm_pipeline_run_id` — UUID linking all Silver rows to one pipeline run
    - `_tdm_source_layer` — always "bronze"
    - `_tdm_masking_applied` — always True for Silver
    - `_tdm_ingested_at` — pipeline timestamp
    """)
    st.code("""
# transform.py
def transform_customer(df):
    parts = F.split(F.col("email"), "@")
    email_domain = F.when(F.size(parts) > 1, parts.getItem(1)).otherwise(F.lit(None))
    return (df
        .withColumnRenamed("first_name", "given_name")
        .withColumnRenamed("last_name",  "family_name")
        .withColumn("email_domain", email_domain))
    """, language="python")

with t_catalog:
    st.markdown("### Unity Catalog Registration")
    st.markdown("""
    **File:** `databricks/src/catalog.py`

    After Silver write, tables are registered in Unity Catalog with:
    - Full 3-part name: `tdm_catalog.tdm_dev.silver_customer`
    - Column-level PII tags (via `COMMENT` clauses)
    - Row count and last-updated metadata
    """)
    st.code("""
# catalog.py
def register_table(spark, catalog, schema, domain, run_id):
    full_name = f"{catalog}.{schema}.silver_{domain}"
    spark.sql(f"ALTER TABLE {full_name} SET TBLPROPERTIES ("
              f"  'tdm.run_id' = '{run_id}', "
              f"  'tdm.masking_applied' = 'true')")
    """, language="python")

with t_api:
    st.markdown("### FastAPI Backend")
    st.markdown("""
    **Directory:** `backend/app/routers/`

    Exposes the TDM platform capabilities as a REST API:

    | Endpoint | Description |
    |---|---|
    | `GET /health` | Service health check |
    | `GET /domains/` | Domain schema + PII + compliance tags |
    | `GET /datasets/` | Available test datasets |
    | `GET /jobs/` | Job run status (live from Databricks or stub) |
    | `POST /requests/` | Submit test data request |
    | `POST /masking/policies` | Create masking policy |
    | `POST /synthetic/requests` | Request synthetic data generation |
    | `POST /products/compare` | Deckers product comparison |
    | `POST /recommendations` | Scored product recommendations |
    | `GET /lineage/{domain}` | Column-level data lineage |
    """)
