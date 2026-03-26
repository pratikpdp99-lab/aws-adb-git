"""
Shared PySpark session fixture for Databricks unit tests.
Uses a local[2] master so tests run without a real Databricks cluster.
"""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark(tmp_path_factory):
    """Local SparkSession scoped to the entire test session."""
    warehouse = str(tmp_path_factory.mktemp("warehouse"))
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("tdm-test")
        .config("spark.sql.warehouse.dir", warehouse)
        .config("spark.ui.enabled", "false")
        .enableHiveSupport()
        .getOrCreate()
    )
