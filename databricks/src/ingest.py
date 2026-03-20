"""
Source onboarding: reads raw retail data from S3 and writes to Delta (Bronze layer).
Supported domains: customer, order, product, inventory, loyalty
"""

from pyspark.sql import SparkSession, DataFrame
from databricks.src.utils import table_name


SUPPORTED_DOMAINS = ["customer", "order", "product", "inventory", "loyalty"]


def get_spark() -> SparkSession:
    return SparkSession.builder.appName("tdm-ingest").getOrCreate()


def read_source(
    spark: SparkSession,
    path: str,
    format: str = "csv",
    options: dict = None,
) -> DataFrame:
    """Read source data from S3 or local path.
    Defaults to CSV with header + schema inference for sample/test data.
    """
    reader = spark.read.format(format)
    if format == "csv":
        reader = reader.option("header", "true").option("inferSchema", "true")
    for k, v in (options or {}).items():
        reader = reader.option(k, v)
    return reader.load(path)


def read_from_s3(spark: SparkSession, s3_path: str, format: str = "parquet") -> DataFrame:
    """Read source data from S3 (parquet). Use read_source() for CSV."""
    return spark.read.format(format).load(s3_path)


def write_to_bronze(
    df: DataFrame,
    catalog: str,
    schema: str,
    domain: str,
    table_format: str = "delta",
) -> None:
    """Write raw data to Bronze table. Use table_format='parquet' for local tests."""
    if domain not in SUPPORTED_DOMAINS:
        raise ValueError(f"Unsupported domain: {domain}. Must be one of {SUPPORTED_DOMAINS}")
    table = table_name(catalog, schema, f"bronze_{domain}")
    (
        df.write.format(table_format)
        .mode("overwrite")
        .option("mergeSchema", "true")
        .saveAsTable(table)
    )


def run(domain: str, s3_path: str, catalog: str = "tdm_catalog", schema: str = "tdm_dev") -> None:
    spark = get_spark()
    df = read_from_s3(spark, s3_path)
    write_to_bronze(df, catalog, schema, domain)
    print(f"Ingested {df.count()} rows into {catalog}.{schema}.bronze_{domain}")
