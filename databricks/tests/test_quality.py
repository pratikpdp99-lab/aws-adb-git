"""Unit tests for quality.py."""

import pytest
from pyspark.sql import SparkSession
from databricks.src.quality import (
    CompletenessCheck,
    UniquenessCheck,
    ValidityCheck,
    run_dq_checks,
)


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local").appName("tdm-test-quality").getOrCreate()


def test_completeness_passes(spark):
    df = spark.createDataFrame(
        [("CUST-001", "a@b.com"), ("CUST-002", "c@d.com")],
        ["customer_id", "email"],
    )
    result = CompletenessCheck("customer_id").run(df, "customer", "run-1")
    assert result.passed
    assert result.score == 1.0


def test_completeness_fails(spark):
    df = spark.createDataFrame(
        [("CUST-001", "a@b.com"), (None, "c@d.com")],
        ["customer_id", "email"],
    )
    result = CompletenessCheck("customer_id", threshold=0.99).run(df, "customer", "run-1")
    assert not result.passed
    assert result.score == 0.5


def test_uniqueness_passes(spark):
    df = spark.createDataFrame([("CUST-001",), ("CUST-002",)], ["customer_id"])
    result = UniquenessCheck("customer_id").run(df, "customer", "run-1")
    assert result.passed
    assert result.score == 1.0


def test_uniqueness_fails_on_duplicates(spark):
    df = spark.createDataFrame([("CUST-001",), ("CUST-001",)], ["customer_id"])
    result = UniquenessCheck("customer_id").run(df, "customer", "run-1")
    assert not result.passed
    assert result.score == 0.5


def test_validity_email_passes(spark):
    df = spark.createDataFrame(
        [("alice@example.com",), ("bob@test.org",)], ["email"]
    )
    result = ValidityCheck("email", r"^[^@]+@[^@]+\.[^@]+$").run(df, "customer", "run-1")
    assert result.passed
    assert result.score == 1.0


def test_validity_email_fails(spark):
    df = spark.createDataFrame(
        [("not-an-email",), ("bob@test.org",)], ["email"]
    )
    result = ValidityCheck("email", r"^[^@]+@[^@]+\.[^@]+$", threshold=0.99).run(df, "customer", "run-1")
    assert not result.passed


def test_run_dq_checks_customer(spark):
    df = spark.createDataFrame(
        [("CUST-001", "alice@example.com"), ("CUST-002", "bob@test.com")],
        ["customer_id", "email"],
    )
    results = run_dq_checks(df, "customer", "run-1")
    assert len(results) > 0
    assert all(r.domain == "customer" for r in results)
    assert all(r.run_id == "run-1" for r in results)
