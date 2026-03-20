"""Tests for /synthetic endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

_REQ_BODY = {
    "domain":      "product",
    "row_count":   100,
    "environment": "dev",
    "locale":      "en_US",
    "requester":   "test-user",
}


def test_create_synthetic_request():
    r = client.post("/synthetic/requests", json=_REQ_BODY)
    assert r.status_code == 201
    body = r.json()
    assert body["domain"] == "product"
    assert body["row_count"] == 100
    assert body["status"] in ("QUEUED", "RUNNING")
    assert body["id"].startswith("SYN-")


def test_list_synthetic_requests():
    client.post("/synthetic/requests", json=_REQ_BODY)
    r = client.get("/synthetic/requests")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_list_filter_by_domain():
    client.post("/synthetic/requests", json=_REQ_BODY)
    r = client.get("/synthetic/requests?domain=product")
    assert r.status_code == 200
    for req in r.json():
        assert req["domain"] == "product"


def test_get_synthetic_request():
    created = client.post("/synthetic/requests", json=_REQ_BODY).json()
    r = client.get(f"/synthetic/requests/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_synthetic_request_not_found():
    r = client.get("/synthetic/requests/SYN-9999")
    assert r.status_code == 404


def test_cancel_synthetic_request():
    created = client.post("/synthetic/requests", json=_REQ_BODY).json()
    r = client.patch(f"/synthetic/requests/{created['id']}/cancel")
    assert r.status_code == 200
    assert r.json()["status"] == "FAILED"


def test_create_invalid_domain():
    r = client.post("/synthetic/requests", json={**_REQ_BODY, "domain": "bad_domain"})
    assert r.status_code == 422
