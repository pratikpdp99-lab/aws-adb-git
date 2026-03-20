"""Tests for /datasets endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_datasets():
    r = client.get("/datasets/")
    assert r.status_code == 200
    body = r.json()
    assert "datasets" in body
    assert body["total"] >= 0


def test_get_dataset_not_found():
    r = client.get("/datasets/ds-999")
    assert r.status_code == 404


def test_filter_by_domain():
    r = client.get("/datasets/?domain=customer")
    assert r.status_code == 200
    for ds in r.json()["datasets"]:
        assert ds["domain"] == "customer"
