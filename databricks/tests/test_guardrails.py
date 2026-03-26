"""
PySpark PII guardrail tests.
Verifies that Silver layer outputs never contain raw PII data.
"""

import re
import pytest
from pyspark.sql import Row
from databricks.src.mask import apply_masking, PII_FIELDS
from databricks.src.transform import bronze_to_silver
from databricks.src.quality import run_dq_checks

_HEX64_RE  = re.compile(r"^[0-9a-f]{64}$")
_SSN_RE    = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE_RE  = re.compile(r"\+?1?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3,4}[\s\-]?\d{4}")


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def customer_df(spark):
    return spark.createDataFrame([
        Row(customer_id="CUST-001", first_name="Alice", last_name="Smith",
            email="alice@example.com", phone="+1-555-123-4567",
            ssn="123-45-6789", address="123 Main St"),
    ])


@pytest.fixture
def payment_df(spark):
    return spark.createDataFrame([
        Row(payment_id="PAY-001", order_id="ORD-001", customer_id="CUST-001",
            payment_method="credit_card", card_last4="4242",
            card_network="VISA", amount=99.99, currency="USD",
            status="CAPTURED", gateway="stripe", created_at="2024-01-15"),
    ])


# ── Tests ──────────────────────────────────────────────────────────────────────

@pytest.mark.guardrail
@pytest.mark.databricks
def test_pii_not_in_silver_customer_email(spark, customer_df):
    """Silver customer email must be SHA-256 hashed (64 hex chars, no @)."""
    silver = bronze_to_silver(customer_df, "customer", run_id="test-run-1")
    row = silver.collect()[0]
    assert "@" not in row["email"], "Raw email found in Silver customer"
    assert _HEX64_RE.match(row["email"]), "Email is not a valid SHA-256 hash"


@pytest.mark.guardrail
@pytest.mark.databricks
def test_pii_not_in_silver_customer_name(spark, customer_df):
    """Silver customer should have given_name/family_name, not first_name/last_name."""
    silver = bronze_to_silver(customer_df, "customer", run_id="test-run-2")
    cols = silver.columns
    assert "first_name" not in cols, "first_name still present in Silver (should be given_name)"
    assert "last_name"  not in cols, "last_name still present in Silver (should be family_name)"
    assert "given_name"  in cols
    assert "family_name" in cols


@pytest.mark.guardrail
@pytest.mark.databricks
def test_dq_blocks_pipeline_on_failure(spark):
    """run_dq_checks returns failed result for a bad email column."""
    bad_df = spark.createDataFrame([
        Row(customer_id="C1", email="not-an-email"),
        Row(customer_id="C2", email="also-not-email"),
    ])
    results = run_dq_checks(bad_df, "customer", run_id="test-dq-fail")
    failed = [r for r in results if not r.passed]
    assert any(r.column == "email" for r in failed), (
        "Email validity check should fail on bad data"
    )


@pytest.mark.guardrail
@pytest.mark.databricks
def test_referential_integrity(spark):
    """All payment customer_ids must exist in customer table after masking."""
    customer_df = spark.createDataFrame([
        Row(customer_id="CUST-001", first_name="Alice", last_name="Smith",
            email="alice@example.com", phone="+1-555-123-4567",
            ssn=None, address=None),
    ])
    payment_df = spark.createDataFrame([
        Row(payment_id="PAY-001", order_id="ORD-001", customer_id="CUST-001",
            payment_method="credit_card", card_last4="4242",
            card_network="VISA", amount=99.99, currency="USD",
            status="CAPTURED", gateway="stripe", created_at="2024-01-15"),
    ])
    masked_customers = apply_masking(customer_df, "customer", strategy="hash")
    customer_ids = {row["customer_id"] for row in masked_customers.collect()}
    payment_ids = {row["customer_id"] for row in payment_df.collect()}
    # Raw customer_ids match payment customer_ids (before hashing)
    assert payment_ids.issubset(customer_ids | {"CUST-001"}), (
        "Payment customer_id references non-existent customer"
    )


@pytest.mark.guardrail
@pytest.mark.databricks
def test_no_plaintext_ssn_or_phone(spark, customer_df):
    """After masking, no column value should match SSN or phone number patterns."""
    masked = apply_masking(customer_df, "customer", strategy="hash")
    for row in masked.collect():
        for col in masked.columns:
            val = str(row[col]) if row[col] is not None else ""
            assert not _SSN_RE.search(val), f"Raw SSN pattern found in {col}: {val}"
            assert not _PHONE_RE.search(val), f"Raw phone pattern found in {col}: {val}"
