"""Tests for /masking endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

_POLICY_BODY = {
    "domain": "customer",
    "rules": [
        {"field": "email",      "strategy": "hash"},
        {"field": "first_name", "strategy": "redact"},
    ],
    "created_by": "test-user",
}


def test_submit_masking_policy():
    r = client.post("/masking/policies", json=_POLICY_BODY)
    assert r.status_code == 201
    body = r.json()
    assert body["domain"] == "customer"
    assert body["version"] == 1
    assert len(body["rules"]) == 2


def test_list_masking_policies():
    client.post("/masking/policies", json=_POLICY_BODY)
    r = client.get("/masking/policies")
    assert r.status_code == 200
    assert any(p["domain"] == "customer" for p in r.json())


def test_get_masking_policy():
    client.post("/masking/policies", json=_POLICY_BODY)
    r = client.get("/masking/policies/customer")
    assert r.status_code == 200
    assert r.json()["domain"] == "customer"


def test_get_masking_policy_not_found():
    r = client.get("/masking/policies/nonexistent")
    assert r.status_code == 404


def test_update_masking_policy_increments_version():
    client.post("/masking/policies", json=_POLICY_BODY)
    r1 = client.get("/masking/policies/customer")
    v1 = r1.json()["version"]

    r2 = client.put("/masking/policies/customer", json=_POLICY_BODY)
    assert r2.status_code == 200
    assert r2.json()["version"] == v1 + 1


def test_delete_masking_policy():
    client.post("/masking/policies", json={**_POLICY_BODY, "domain": "order",
                                           "rules": [{"field": "customer_id", "strategy": "hash"}]})
    r = client.delete("/masking/policies/order")
    assert r.status_code == 204
    assert client.get("/masking/policies/order").status_code == 404


def test_submit_invalid_domain():
    r = client.post("/masking/policies", json={**_POLICY_BODY, "domain": "invalid"})
    assert r.status_code == 422
