"""Tests for /lineage endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.connectors import get_databricks_optional

client = TestClient(app)

# No Databricks — use schema-derived placeholders only
app.dependency_overrides[get_databricks_optional] = lambda: None


def test_get_domain_lineage_customer():
    r = client.get("/lineage/customer")
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "customer"
    assert body["table"] == "silver_customer"
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2


def test_lineage_nodes_contain_s3_bronze_silver():
    r = client.get("/lineage/order")
    nodes = {n["type"]: n for n in r.json()["nodes"]}
    assert "s3" in nodes
    assert "bronze" in nodes
    assert "silver" in nodes


def test_lineage_edges_sequence():
    r = client.get("/lineage/product")
    edges = r.json()["edges"]
    transforms = {e["transform"] for e in edges}
    assert "ingest" in transforms
    assert "mask+transform" in transforms


def test_lineage_pii_columns_customer():
    r = client.get("/lineage/customer")
    columns = {c["column"]: c for c in r.json()["columns"]}
    # given_name maps back to first_name (PII)
    assert columns["given_name"]["pii"] is True
    assert columns["given_name"]["source_column"] == "first_name"
    # customer_id is not PII
    assert columns["customer_id"]["pii"] is False


def test_lineage_product_no_pii():
    r = client.get("/lineage/product")
    for col in r.json()["columns"]:
        assert col["pii"] is False


def test_get_domain_lineage_not_found():
    r = client.get("/lineage/nonexistent")
    assert r.status_code == 404


def test_get_table_lineage():
    r = client.get("/lineage/customer/bronze_customer")
    assert r.status_code == 200
    assert r.json()["table"] == "bronze_customer"


def test_lineage_with_pipeline_run_id():
    r = client.get("/lineage/loyalty?pipeline_run_id=abc-999")
    assert r.status_code == 200
    assert r.json()["pipeline_run_id"] == "abc-999"
