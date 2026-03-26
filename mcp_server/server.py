"""
TDM MCP server — exposes TDM platform capabilities as MCP tools.

Run:
    mcp run mcp_server/server.py

Tools available:
    list_domains, get_schema, get_lineage, get_recent_jobs,
    get_masking_policy, compare_products
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

_BASE    = os.getenv("TDM_API_URL", "http://localhost:8000")
_TIMEOUT = 15

mcp = FastMCP("tdm-deckers")


def _get(path: str, params: dict | None = None) -> dict | list:
    with httpx.Client(base_url=_BASE, timeout=_TIMEOUT) as client:
        r = client.get(path, params=params)
        r.raise_for_status()
        return r.json()


def _post(path: str, json: dict) -> dict | list:
    with httpx.Client(base_url=_BASE, timeout=_TIMEOUT) as client:
        r = client.post(path, json=json)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def list_domains() -> list[dict]:
    """List all TDM data domains with their field schemas and PII tags."""
    data = _get("/domains/")
    return data.get("domains", [])


@mcp.tool()
def get_schema(domain: str) -> dict:
    """Get the full schema for a specific TDM domain including compliance tags.

    Args:
        domain: Domain name (customer, order, product, inventory, loyalty, payment)
    """
    return _get(f"/domains/{domain}")


@mcp.tool()
def get_lineage(domain: str) -> dict:
    """Get data lineage graph for a domain showing S3 → Bronze → Silver flow.

    Args:
        domain: Domain name
    """
    return _get(f"/lineage/{domain}")


@mcp.tool()
def get_recent_jobs(limit: int = 10) -> list[dict]:
    """Get recent TDM pipeline job runs with status.

    Args:
        limit: Maximum number of runs to return (default 10)
    """
    data = _get("/jobs/", params={"limit": limit})
    return data.get("runs", [])


@mcp.tool()
def get_masking_policy(domain: str) -> dict:
    """Get the active masking policy for a domain.

    Args:
        domain: Domain name
    """
    return _get(f"/masking/policies/{domain}")


@mcp.tool()
def compare_products(product_ids: list[str]) -> dict:
    """Compare 2–4 Deckers products side by side.

    Args:
        product_ids: List of 2–4 product IDs (e.g. ["UGG-001", "HOK-001"])
    """
    return _post("/products/compare", json={"product_ids": product_ids})


@mcp.tool()
def list_datasets() -> list[dict]:
    """List all available test datasets provisioned on the TDM platform."""
    data = _get("/datasets/")
    return data.get("datasets", [])


@mcp.tool()
def health_check() -> dict:
    """Check the health of the TDM FastAPI backend."""
    return _get("/health")


if __name__ == "__main__":
    mcp.run()
