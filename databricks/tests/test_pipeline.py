"""
Integration test for pipeline.py using local sample CSV files.
Runs the full ingest → DQ → transform flow without S3 or Unity Catalog.
Uses catalog="" so table names are 2-part (schema.table) for local Hive metastore.
"""

import os
import pytest
from pyspark.sql import SparkSession
from databricks.src.pipeline import run_pipeline

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../sample_data")

# Shared test params — empty catalog for local 2-part table names
_CATALOG = ""
_SCHEMA  = "tdm_local_test"
_OPTS    = dict(catalog=_CATALOG, schema=_SCHEMA, skip_dq_fail=True, skip_catalog=True, table_format="parquet")


@pytest.fixture(scope="session")
def spark():
    s = (
        SparkSession.builder
        .master("local")
        .appName("tdm-test-pipeline")
        .config("spark.sql.warehouse.dir", "/tmp/tdm_test_warehouse")
        .enableHiveSupport()
        .getOrCreate()
    )
    s.sql(f"CREATE DATABASE IF NOT EXISTS {_SCHEMA}")
    return s


@pytest.fixture(scope="session")
def s3_paths():
    return {
        "customer": os.path.join(SAMPLE_DIR, "customer_sample.csv"),
        "order":    os.path.join(SAMPLE_DIR, "order_sample.csv"),
        "product":  os.path.join(SAMPLE_DIR, "product_sample.csv"),
    }


def test_pipeline_runs_end_to_end(spark, s3_paths):
    run_id = run_pipeline(spark, s3_paths=s3_paths, **_OPTS)
    assert run_id is not None
    assert len(run_id) == 36  # UUID format


def test_pipeline_silver_tables_created(spark, s3_paths):
    run_pipeline(spark, s3_paths=s3_paths, **_OPTS)
    for domain in ["customer", "order", "product"]:
        silver = spark.table(f"{_SCHEMA}.silver_{domain}")
        assert silver.count() > 0
        assert "_tdm_pipeline_run_id" in silver.columns
        assert "_tdm_masking_applied" in silver.columns


def test_pipeline_customer_pii_masked(spark, s3_paths):
    run_pipeline(spark, s3_paths={"customer": s3_paths["customer"]}, **_OPTS)
    silver = spark.table(f"{_SCHEMA}.silver_customer")
    row = silver.collect()[0]
    # email should be SHA-256 hashed — no @ present
    assert "@" not in row["email"]
