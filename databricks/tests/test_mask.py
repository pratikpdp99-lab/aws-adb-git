"""Unit tests for mask.py — run locally with pytest + pyspark."""

import pytest
from pyspark.sql import SparkSession
from databricks.src.mask import apply_masking, hash_column, mask_column


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local").appName("tdm-test").getOrCreate()


def test_hash_column(spark):
    df = spark.createDataFrame([("test@example.com",)], ["email"])
    result = hash_column(df, "email")
    val = result.collect()[0]["email"]
    assert val != "test@example.com"
    assert len(val) == 64  # SHA-256 hex


def test_mask_column(spark):
    df = spark.createDataFrame([("secret",)], ["ssn"])
    result = mask_column(df, "ssn")
    assert result.collect()[0]["ssn"] == "***MASKED***"


def test_apply_masking_customer(spark):
    df = spark.createDataFrame(
        [("alice@example.com", "555-1234", "Alice", "Smith")],
        ["email", "phone", "first_name", "last_name"],
    )
    result = apply_masking(df, "customer", strategy="hash")
    row = result.collect()[0]
    assert row["email"] != "alice@example.com"
    assert row["first_name"] != "Alice"
