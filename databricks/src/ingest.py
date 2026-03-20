"""
Source onboarding: reads raw retail data from S3 and writes to Delta (Bronze layer).
Supported domains: customer, order, product, inventory, loyalty
"""

from pyspark.sql import SparkSession, DataFrame


SUPPORTED_DOMAINS = ["customer", "order", "product", "inventory", "loyalty"]


def get_spark() -> SparkSession:
    return SparkSession.builder.appName("tdm-ingest").getOrCreate()


def read_from_s3(spark: SparkSession, s3_path: str, format: str = "parquet") -> DataFrame:
    """Read source data from S3."""
    return spark.read.format(format).load(s3_path)


def write_to_bronze(df: DataFrame, catalog: str, schema: str, domain: str) -> None:
    """Write raw data to Bronze Delta table."""
    if domain not in SUPPORTED_DOMAINS:
        raise ValueError(f"Unsupported domain: {domain}. Must be one of {SUPPORTED_DOMAINS}")
    table = f"{catalog}.{schema}.bronze_{domain}"
    (
        df.write.format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table)
    )


def run(domain: str, s3_path: str, catalog: str = "tdm_catalog", schema: str = "tdm_dev") -> None:
    spark = get_spark()
    df = read_from_s3(spark, s3_path)
    write_to_bronze(df, catalog, schema, domain)
    print(f"Ingested {df.count()} rows into {catalog}.{schema}.bronze_{domain}")
