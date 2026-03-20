"""Unit tests for transform.py."""

import pytest
from pyspark.sql import SparkSession
from databricks.src.transform import bronze_to_silver, add_lineage_metadata, transform_customer


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local").appName("tdm-test-transform").getOrCreate()


def test_add_lineage_metadata(spark):
    df = spark.createDataFrame([("CUST-001",)], ["customer_id"])
    result = add_lineage_metadata(df, run_id="test-run-001")
    assert "_tdm_pipeline_run_id" in result.columns
    assert "_tdm_ingested_at"     in result.columns
    assert "_tdm_masking_applied" in result.columns
    row = result.collect()[0]
    assert row["_tdm_pipeline_run_id"] == "test-run-001"
    assert row["_tdm_masking_applied"] is True


def test_transform_customer_renames_columns(spark):
    df = spark.createDataFrame(
        [("CUST-001", "Alice", "Smith", "alice@example.com", "+1-555-1234", "2024-01-01")],
        ["customer_id", "first_name", "last_name", "email", "phone", "created_date"],
    )
    result = transform_customer(df)
    assert "given_name"    in result.columns
    assert "family_name"   in result.columns
    assert "email_domain"  in result.columns
    assert "first_name" not in result.columns
    assert result.collect()[0]["email_domain"] == "example.com"


def test_bronze_to_silver_customer_masking(spark):
    df = spark.createDataFrame(
        [("CUST-001", "Alice", "Smith", "alice@example.com", "+1-555-1234", "2024-01-01")],
        ["customer_id", "first_name", "last_name", "email", "phone", "created_date"],
    )
    result = bronze_to_silver(df, "customer", run_id="run-abc", mask=True)
    row = result.collect()[0]
    # PII fields should be hashed
    assert row["email"]       != "alice@example.com"
    assert row["given_name"]  != "Alice"   # renamed + hashed
    # Lineage present
    assert row["_tdm_pipeline_run_id"] == "run-abc"


def test_bronze_to_silver_no_mask(spark):
    df = spark.createDataFrame(
        [("CUST-001", "Alice", "Smith", "alice@example.com", "+1-555-1234", "2024-01-01")],
        ["customer_id", "first_name", "last_name", "email", "phone", "created_date"],
    )
    result = bronze_to_silver(df, "customer", run_id="run-xyz", mask=False)
    row = result.collect()[0]
    # Email not hashed when mask=False (but column is renamed by transform_customer)
    assert row["email"] == "alice@example.com"


def test_bronze_to_silver_order(spark):
    df = spark.createDataFrame(
        [("ORD-001", "CUST-001", "2024-01-20", "125.50", "DELIVERED")],
        ["order_id", "customer_id", "order_date", "total_amount", "status"],
    )
    result = bronze_to_silver(df, "order", run_id="run-order-1")
    row = result.collect()[0]
    assert row["total_amount"] == 125.50
    assert "_tdm_pipeline_run_id" in result.columns


def test_bronze_to_silver_product(spark):
    df = spark.createDataFrame(
        [("PROD-001", "Running Shoes", "Footwear", "89.99", "true")],
        ["product_id", "name", "category", "price", "in_stock"],
    )
    result = bronze_to_silver(df, "product", run_id="run-prod-1")
    row = result.collect()[0]
    assert row["price"] == 89.99
    assert row["name_upper"] == "RUNNING SHOES"
