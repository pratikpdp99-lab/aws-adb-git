"""Tests for /domains endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_domains():
    r = client.get("/domains/")
    assert r.status_code == 200
    body = r.json()
    assert "domains" in body
    assert body["total"] == 6


def test_list_domains_filter_pii():
    r = client.get("/domains/?has_pii=true")
    assert r.status_code == 200
    for d in r.json()["domains"]:
        assert len(d["pii_fields"]) > 0


def test_list_domains_filter_no_pii():
    r = client.get("/domains/?has_pii=false")
    assert r.status_code == 200
    for d in r.json()["domains"]:
        assert d["pii_fields"] == []


def test_get_domain_customer():
    r = client.get("/domains/customer")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "customer"
    assert "first_name" in body["pii_fields"]
    assert any(f["name"] == "email" for f in body["fields"])


def test_get_domain_not_found():
    r = client.get("/domains/nonexistent")
    assert r.status_code == 404


def test_get_domain_product_no_pii():
    r = client.get("/domains/product")
    assert r.status_code == 200
    assert r.json()["pii_fields"] == []
