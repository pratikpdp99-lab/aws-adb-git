"""
Bronze → Silver transformations.
Applies masking, domain-specific standardisation, and TDM lineage metadata columns.
All Silver tables carry _tdm_* columns for lineage traceability in Unity Catalog.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from databricks.src.mask import apply_masking
from databricks.src.utils import table_name


# ── Lineage metadata ──────────────────────────────────────────────────────────

def add_lineage_metadata(df: DataFrame, run_id: str, source_layer: str = "bronze") -> DataFrame:
    """Attach TDM lineage columns to every Silver row."""
    return (
        df.withColumn("_tdm_pipeline_run_id", F.lit(run_id))
          .withColumn("_tdm_source_layer",    F.lit(source_layer))
          .withColumn("_tdm_masking_applied", F.lit(True))
          .withColumn("_tdm_ingested_at",     F.current_timestamp())
    )


# ── Domain transforms ─────────────────────────────────────────────────────────

def transform_customer(df: DataFrame) -> DataFrame:
    # email may be hashed at this point — extract domain only if @ is present
    parts = F.split(F.col("email"), "@")
    email_domain = F.when(F.size(parts) > 1, parts.getItem(1)).otherwise(F.lit(None))
    return (
        df.withColumnRenamed("first_name", "given_name")
          .withColumnRenamed("last_name",  "family_name")
          .withColumn("email_domain", email_domain)
    )


def transform_order(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("order_date",    F.to_date(F.col("order_date")))
          .withColumn("total_amount",  F.col("total_amount").cast("double"))
    )


def transform_product(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("price",      F.col("price").cast("double"))
          .withColumn("name_upper", F.upper(F.col("name")))
    )


_TRANSFORMS = {
    "customer": transform_customer,
    "order":    transform_order,
    "product":  transform_product,
}


# ── Main entry point ──────────────────────────────────────────────────────────

def bronze_to_silver(
    df: DataFrame,
    domain: str,
    run_id: str,
    mask: bool = True,
    masking_strategy: str = "hash",
) -> DataFrame:
    """Apply masking → domain transform → lineage metadata."""
    if mask:
        df = apply_masking(df, domain, strategy=masking_strategy)
    transform_fn = _TRANSFORMS.get(domain)
    if transform_fn:
        df = transform_fn(df)
    return add_lineage_metadata(df, run_id=run_id)


def write_silver(
    df: DataFrame,
    catalog: str,
    schema: str,
    domain: str,
    table_format: str = "delta",
) -> None:
    table = table_name(catalog, schema, f"silver_{domain}")
    (
        df.write.format(table_format)
          .mode("overwrite")
          .option("overwriteSchema", "true")
          .saveAsTable(table)
    )
    print(f"Silver written: {table} ({df.count()} rows)")
