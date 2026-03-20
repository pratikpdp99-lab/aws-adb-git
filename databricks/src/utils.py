"""Shared utility helpers for TDM pipeline modules."""


def table_name(catalog: str, schema: str, table: str) -> str:
    """Build a fully qualified table name.
    Uses 3-part name (catalog.schema.table) on Databricks.
    Falls back to 2-part (schema.table) when catalog is empty — for local Spark.
    """
    if catalog:
        return f"{catalog}.{schema}.{table}"
    return f"{schema}.{table}"
