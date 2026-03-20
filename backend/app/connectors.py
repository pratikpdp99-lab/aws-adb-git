"""
Config-driven connector factory for Databricks and AWS.
Injected into routers via FastAPI Depends — never instantiated directly.
Returns None-safe stubs when credentials are absent (local dev without workspace).
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
import boto3
from databricks.sdk import WorkspaceClient

from backend.app.config import Settings, get_settings


# ── Databricks ────────────────────────────────────────────────────────────────

def get_databricks(
    settings: Settings = Depends(get_settings),
) -> WorkspaceClient:
    """Return an authenticated Databricks WorkspaceClient.
    Raises 503 if credentials are not configured.
    """
    if not settings.databricks_host or not settings.databricks_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Databricks credentials not configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN.",
        )
    return WorkspaceClient(
        host=settings.databricks_host,
        token=settings.databricks_token,
    )


def get_databricks_optional(
    settings: Settings = Depends(get_settings),
) -> Optional[WorkspaceClient]:
    """Return WorkspaceClient or None (does not raise — used for non-critical calls)."""
    if not settings.databricks_host or not settings.databricks_token:
        return None
    return WorkspaceClient(
        host=settings.databricks_host,
        token=settings.databricks_token,
    )


# ── AWS ───────────────────────────────────────────────────────────────────────

def get_aws_session(
    settings: Settings = Depends(get_settings),
) -> boto3.Session:
    """Return a boto3 Session using ~/.aws/credentials (aws configure)."""
    return boto3.Session(region_name=settings.aws_region)


def get_s3(
    session: boto3.Session = Depends(get_aws_session),
) -> boto3.client:
    """Return an S3 client."""
    return session.client("s3")
