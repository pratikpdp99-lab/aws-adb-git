"""
Shared test fixtures for backend API tests.
Provides TestClient and state-reset for all in-memory routers.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import backend.app.routers.requests as req_router
import backend.app.routers.masking as mask_router
import backend.app.routers.synthetic as syn_router


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all in-memory state between tests to ensure isolation."""
    req_router._REQUESTS.clear()
    req_router._counter = 1
    mask_router._POLICIES.clear()
    mask_router._counter = 1
    syn_router._REQUESTS.clear()
    syn_router._counter = 1
    yield
    req_router._REQUESTS.clear()
    req_router._counter = 1
    mask_router._POLICIES.clear()
    mask_router._counter = 1
    syn_router._REQUESTS.clear()
    syn_router._counter = 1


@pytest.fixture
def client():
    """Return a TestClient with Databricks dependency stubbed out."""
    from backend.app.main import app
    with patch("backend.app.connectors.get_databricks_optional", return_value=lambda: None):
        yield TestClient(app)
