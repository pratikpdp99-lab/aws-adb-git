"""
Thin HTTP wrapper around the TDM FastAPI backend.
All methods return parsed JSON dicts/lists; raise on non-2xx.
"""

import os
import requests

_BASE = os.getenv("TDM_API_URL", "http://localhost:8000")
_TIMEOUT = 10


def _get(path: str, params: dict | None = None) -> dict | list:
    r = requests.get(f"{_BASE}{path}", params=params, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, json: dict | None = None) -> dict | list:
    r = requests.post(f"{_BASE}{path}", json=json, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _patch(path: str, json: dict | None = None) -> dict | list:
    r = requests.patch(f"{_BASE}{path}", json=json, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


# ── API helpers ────────────────────────────────────────────────────────────────

def health() -> dict:
    return _get("/health")


def list_domains(has_pii: bool | None = None) -> dict:
    params = {}
    if has_pii is not None:
        params["has_pii"] = str(has_pii).lower()
    return _get("/domains/", params=params)


def get_domain(name: str) -> dict:
    return _get(f"/domains/{name}")


def list_datasets() -> dict:
    return _get("/datasets/")


def list_jobs(limit: int = 20) -> dict:
    return _get("/jobs/", params={"limit": limit})


def get_job(run_id: str) -> dict:
    return _get(f"/jobs/{run_id}")


def trigger_job(job_id: str, params: dict | None = None) -> dict:
    return _post("/jobs/trigger", json={"job_id": job_id, "params": params or {}})


def list_requests(status: str | None = None) -> list:
    params = {}
    if status:
        params["status"] = status
    return _get("/requests/", params=params)


def create_request(requester: str, domain: str, environment: str,
                   row_count: int, purpose: str | None = None) -> dict:
    return _post("/requests/", json={
        "requester": requester, "domain": domain,
        "environment": environment, "row_count": row_count, "purpose": purpose,
    })


def approve_request(request_id: str) -> dict:
    return _patch(f"/requests/{request_id}/approve")


def list_masking_policies() -> list:
    return _get("/masking/policies")


def list_synthetic_requests(domain: str | None = None) -> list:
    params = {}
    if domain:
        params["domain"] = domain
    return _get("/synthetic/requests", params=params)


def list_products(brand: str | None = None, in_stock: bool | None = None) -> dict:
    params = {}
    if brand:
        params["brand"] = brand
    if in_stock is not None:
        params["in_stock"] = str(in_stock).lower()
    return _get("/products/", params=params)


def compare_products(product_ids: list[str]) -> dict:
    return _post("/products/compare", json={"product_ids": product_ids})


def get_lineage(domain: str) -> dict:
    return _get(f"/lineage/{domain}")


def get_recommendations(payload: dict) -> dict:
    return _post("/products/recommendations", json=payload)
