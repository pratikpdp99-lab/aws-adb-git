"""Tests for /jobs endpoints (stub mode — no Databricks credentials required)."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
from backend.app.connectors import get_databricks_optional

client = TestClient(app)


# Force stub mode by overriding the optional Databricks dependency
app.dependency_overrides[get_databricks_optional] = lambda: None


def test_list_jobs_stub():
    r = client.get("/jobs/")
    assert r.status_code == 200
    body = r.json()
    assert "runs" in body
    assert body["total"] >= 1


def test_get_job_run_stub():
    r = client.get("/jobs/1001")
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] == "1001"
    assert body["status"] == "SUCCESS"


def test_get_job_run_not_found_stub():
    r = client.get("/jobs/9999")
    assert r.status_code == 404


def test_trigger_job_requires_databricks():
    # Without real Databricks credentials the trigger endpoint raises 503
    r = client.post("/jobs/trigger", json={"job_id": "stub-001"})
    assert r.status_code in (503, 502, 422)
