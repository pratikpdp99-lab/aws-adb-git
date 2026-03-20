"""
Data subsetting with referential integrity.
Extracts a consistent slice of data across related domain tables.
"""

from pyspark.sql import SparkSession, DataFrame


def get_spark() -> SparkSession:
    return SparkSession.builder.appName("tdm-subset").getOrCreate()


def subset_by_customer_ids(
    spark: SparkSession,
    catalog: str,
    schema: str,
    customer_ids: list,
) -> dict[str, DataFrame]:
    """
    Extract a referentially consistent subset anchored on a list of customer IDs.
    Returns a dict of {domain: DataFrame}.
    """
    id_list = ", ".join(f"'{cid}'" for cid in customer_ids)

    subsets = {}

    subsets["customer"] = spark.sql(
        f"SELECT * FROM {catalog}.{schema}.silver_customer WHERE customer_id IN ({id_list})"
    )
    subsets["order"] = spark.sql(
        f"SELECT * FROM {catalog}.{schema}.silver_order WHERE customer_id IN ({id_list})"
    )
    subsets["loyalty"] = spark.sql(
        f"SELECT * FROM {catalog}.{schema}.silver_loyalty WHERE customer_id IN ({id_list})"
    )

    return subsets


def write_subsets(subsets: dict[str, DataFrame], catalog: str, target_schema: str) -> None:
    """Write subset DataFrames to a target schema (e.g. tdm_lower_env)."""
    for domain, df in subsets.items():
        table = f"{catalog}.{target_schema}.subset_{domain}"
        df.write.format("delta").mode("overwrite").saveAsTable(table)
        print(f"Written {df.count()} rows to {table}")
