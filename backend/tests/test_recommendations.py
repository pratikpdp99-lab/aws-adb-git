"""Tests for /products and /recommendations endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# ── Product listing ────────────────────────────────────────────────────────────

def test_list_products_no_filter():
    r = client.get("/products/")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 17
    assert len(body["products"]) == 17


def test_list_products_brand_filter():
    r = client.get("/products/?brand=UGG")
    assert r.status_code == 200
    body = r.json()
    for p in body["products"]:
        assert p["brand"] == "UGG"


def test_list_products_in_stock_filter():
    r = client.get("/products/?in_stock=true")
    assert r.status_code == 200
    for p in r.json()["products"]:
        assert p["in_stock"] is True


# ── Single product ─────────────────────────────────────────────────────────────

def test_get_product_by_id():
    r = client.get("/products/UGG-001")
    assert r.status_code == 200
    body = r.json()
    assert body["product_id"] == "UGG-001"
    assert body["brand"] == "UGG"


def test_get_product_not_found():
    r = client.get("/products/FAKE-999")
    assert r.status_code == 404


# ── Compare ────────────────────────────────────────────────────────────────────

def test_compare_products_valid():
    r = client.post("/products/compare", json={"product_ids": ["UGG-001", "HOK-001"]})
    assert r.status_code == 200
    body = r.json()
    assert "matrix" in body
    assert "recommended_winner" in body
    assert len(body["products"]) == 2


def test_compare_too_few_products():
    r = client.post("/products/compare", json={"product_ids": ["UGG-001"]})
    assert r.status_code == 400


def test_compare_too_many_products():
    r = client.post("/products/compare", json={"product_ids": ["UGG-001", "UGG-002", "HOK-001", "HOK-002", "TEV-001"]})
    assert r.status_code == 400


# ── Recommendations ────────────────────────────────────────────────────────────

def test_recommendations_returns_scored_list():
    r = client.post("/products/recommendations", json={})
    assert r.status_code == 200
    body = r.json()
    assert "recommendations" in body
    assert len(body["recommendations"]) > 0
    for rec in body["recommendations"]:
        assert "score" in rec
        assert 0.0 <= rec["score"] <= 100.0
        assert "match_reasons" in rec
        assert "product" in rec


def test_recommendations_budget_filter():
    r = client.post("/products/recommendations", json={"budget_max": 50})
    assert r.status_code == 200
    body = r.json()
    # Verify context_summary mentions budget
    assert "budget" in body["context_summary"].lower()
    # All recommendations should have valid scores
    for rec in body["recommendations"]:
        assert 0.0 <= rec["score"] <= 100.0
