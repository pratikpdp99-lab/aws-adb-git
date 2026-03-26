"""
Compliance tag validation tests.
Ensures all PII fields across all domains carry recognised regulatory tags.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

KNOWN_TAGS = {"GDPR", "CCPA", "SOC2", "HIPAA", "PCI"}


@pytest.mark.guardrail
def test_all_pii_fields_have_compliance_tags():
    """Every PII field in every domain must have at least one compliance tag."""
    r = client.get("/domains/")
    assert r.status_code == 200
    for domain in r.json()["domains"]:
        field_map = {f["name"]: f for f in domain["fields"]}
        for pii_field in domain["pii_fields"]:
            field = field_map[pii_field]
            tags = set(field.get("compliance_tags", []))
            assert tags, (
                f"Domain '{domain['name']}' PII field '{pii_field}' has no compliance_tags"
            )
            assert tags & KNOWN_TAGS, (
                f"Domain '{domain['name']}' field '{pii_field}' tags {tags} "
                f"are not in known set {KNOWN_TAGS}"
            )


@pytest.mark.guardrail
def test_compliance_tags_valid_values():
    """compliance_tags values must be from the approved regulatory set."""
    r = client.get("/domains/")
    assert r.status_code == 200
    for domain in r.json()["domains"]:
        for field in domain["fields"]:
            for tag in field.get("compliance_tags", []):
                assert tag in KNOWN_TAGS, (
                    f"Unknown compliance tag '{tag}' on field "
                    f"'{domain['name']}.{field['name']}'"
                )


@pytest.mark.guardrail
def test_customer_email_gdpr_ccpa():
    """customer.email must have both GDPR and CCPA tags."""
    r = client.get("/domains/customer")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    email_tags = set(fields["email"]["compliance_tags"])
    assert "GDPR" in email_tags
    assert "CCPA" in email_tags


@pytest.mark.guardrail
def test_customer_ssn_has_hipaa():
    """customer.ssn must have HIPAA tag in addition to GDPR/CCPA."""
    r = client.get("/domains/customer")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    ssn_tags = set(fields["ssn"]["compliance_tags"])
    assert "HIPAA" in ssn_tags


@pytest.mark.guardrail
def test_payment_card_last4_pci():
    """payment.card_last4 must carry PCI compliance tag."""
    r = client.get("/domains/payment")
    assert r.status_code == 200
    fields = {f["name"]: f for f in r.json()["fields"]}
    assert "PCI" in fields["card_last4"]["compliance_tags"]


@pytest.mark.guardrail
def test_non_pii_fields_no_compliance_tags_required():
    """Non-PII fields without compliance tags should not raise errors."""
    r = client.get("/domains/product")
    assert r.status_code == 200
    # product domain has no PII — compliance tags are optional
    for field in r.json()["fields"]:
        assert field["pii"] is False
