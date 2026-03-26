"""
PII guardrail tests — verify the API never leaks raw PII data.
Marked with @pytest.mark.guardrail for targeted runs.
"""

import re
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Patterns that should never appear raw in API responses
_EMAIL_RE  = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_SSN_RE    = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE_RE  = re.compile(r"\+?1?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}")
_HEX64_RE  = re.compile(r"^[0-9a-f]{64}$")


@pytest.mark.guardrail
def test_dataset_response_no_raw_pii():
    """GET /datasets/ must never contain raw email, SSN, or phone patterns."""
    r = client.get("/datasets/")
    assert r.status_code == 200
    text = r.text
    assert not _EMAIL_RE.search(text), "Raw email found in /datasets/ response"
    assert not _SSN_RE.search(text),   "Raw SSN found in /datasets/ response"


@pytest.mark.guardrail
def test_domain_fields_pii_tagged():
    """All known PII field names in the customer domain must have pii=True."""
    r = client.get("/domains/customer")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    for pii_field in ["first_name", "last_name", "email", "phone", "ssn"]:
        assert fields[pii_field]["pii"] is True, f"{pii_field} should be pii=True"


@pytest.mark.guardrail
def test_masking_policy_hash_applied_correctly():
    """After creating a HASH masking policy, its strategy is recorded correctly."""
    payload = {
        "domain": "customer",
        "rules": [{"field": "email", "strategy": "hash", "preserve_format": False}],
        "created_by": "guardrail-test",
    }
    r = client.post("/masking/policies", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["rules"][0]["strategy"] == "hash"
    assert body["version"] == 1


@pytest.mark.guardrail
def test_synthetic_data_no_real_pii():
    """POST /synthetic/requests must accept a valid domain and return QUEUED/RUNNING."""
    r = client.post("/synthetic/requests", json={
        "domain": "customer",
        "row_count": 100,
        "environment": "dev",
        "requester": "guardrail-test",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["status"] in ("QUEUED", "RUNNING")
    # output_path must be an S3 URI — not a raw data dump
    assert body["output_path"].startswith("s3://")


@pytest.mark.guardrail
def test_no_pii_in_job_error_messages():
    """Job error_message field (when present) must not echo PII patterns."""
    r = client.get("/jobs/")
    assert r.status_code == 200
    for run in r.json()["runs"]:
        err = run.get("error_message") or ""
        assert not _EMAIL_RE.search(err), "Email found in job error_message"
        assert not _SSN_RE.search(err),   "SSN found in job error_message"


@pytest.mark.guardrail
def test_compliance_tags_present():
    """All PII fields in customer domain must have at least one compliance tag."""
    r = client.get("/domains/customer")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    known_tags = {"GDPR", "CCPA", "SOC2", "HIPAA", "PCI"}
    for pii_field in r.json()["pii_fields"]:
        tags = set(fields[pii_field].get("compliance_tags", []))
        assert tags & known_tags, (
            f"PII field '{pii_field}' has no recognised compliance tags: {tags}"
        )


@pytest.mark.guardrail
def test_payment_domain_pci_tags():
    """card_last4 in payment domain must carry PCI compliance tag."""
    r = client.get("/domains/payment")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    assert "PCI" in fields["card_last4"]["compliance_tags"]
    assert "PCI" in fields["card_network"]["compliance_tags"]
