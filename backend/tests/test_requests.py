"""Tests for /requests endpoints."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

_PAYLOAD = {
    "requester": "qa-team",
    "domain": "customer",
    "environment": "dev",
    "row_count": 1000,
}


def test_create_request():
    r = client.post("/requests/", json=_PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "PENDING"
    assert body["id"].startswith("REQ-")


def test_approve_request():
    r = client.post("/requests/", json=_PAYLOAD)
    req_id = r.json()["id"]
    r2 = client.patch(f"/requests/{req_id}/approve")
    assert r2.status_code == 200
    assert r2.json()["status"] == "APPROVED"


def test_get_request_not_found():
    r = client.get("/requests/REQ-9999")
    assert r.status_code == 404
