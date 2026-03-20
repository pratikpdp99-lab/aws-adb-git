"""
Synthetic data generation request endpoints.
Submits generation requests which are fulfilled by the Databricks pipeline.
Optionally triggers a Databricks job run when credentials are configured.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from databricks.sdk import WorkspaceClient

from backend.app.models import SyntheticRequest, SyntheticRequestCreate, SyntheticStatus, SUPPORTED_DOMAINS
from backend.app.config import Settings, get_settings
from backend.app.connectors import get_databricks_optional

router = APIRouter()

_REQUESTS: dict[str, SyntheticRequest] = {}
_counter = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s3_output_path(settings: Settings, domain: str, req_id: str) -> str:
    return f"s3://{settings.tdm_s3_bucket}/synthetic/{domain}/{req_id}/"


@router.post("/requests", response_model=SyntheticRequest, status_code=201)
def create_synthetic_request(
    body: SyntheticRequestCreate,
    settings: Settings = Depends(get_settings),
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
):
    """Submit a synthetic data generation request.
    If a Databricks pipeline job is configured, triggers a job run automatically.
    """
    global _counter
    if body.domain not in SUPPORTED_DOMAINS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported domain '{body.domain}'. Must be one of {SUPPORTED_DOMAINS}.",
        )

    req_id    = f"SYN-{_counter:04d}"
    _counter += 1

    job_run_id: Optional[str] = None
    status = SyntheticStatus.QUEUED

    # Trigger Databricks job run if configured
    if db and settings.tdm_pipeline_job_id:
        try:
            run = db.jobs.run_now(
                job_id=int(settings.tdm_pipeline_job_id),
                job_parameters={
                    "domain":      body.domain,
                    "row_count":   str(body.row_count),
                    "environment": body.environment,
                    "request_id":  req_id,
                    "mode":        "synthetic",
                },
            )
            job_run_id = str(run.run_id)
            status     = SyntheticStatus.RUNNING
        except Exception as e:
            # Job trigger failure is non-fatal — request is still queued
            status = SyntheticStatus.QUEUED

    req = SyntheticRequest(
        id=req_id,
        domain=body.domain,
        row_count=body.row_count,
        environment=body.environment,
        locale=body.locale,
        seed=body.seed,
        requester=body.requester,
        status=status,
        output_path=_s3_output_path(settings, body.domain, req_id),
        job_run_id=job_run_id,
        created_at=_now(),
    )
    _REQUESTS[req_id] = req
    return req


@router.get("/requests", response_model=list[SyntheticRequest])
def list_synthetic_requests(
    domain: str = None,
    status: SyntheticStatus = None,
):
    """List all synthetic data requests, optionally filtered by domain or status."""
    results = list(_REQUESTS.values())
    if domain:
        results = [r for r in results if r.domain == domain]
    if status:
        results = [r for r in results if r.status == status]
    return results


@router.get("/requests/{request_id}", response_model=SyntheticRequest)
def get_synthetic_request(
    request_id: str,
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
):
    """Get a synthetic request and refresh its status from Databricks if a run ID is set."""
    req = _REQUESTS.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Synthetic request '{request_id}' not found.")

    # Refresh status from Databricks if we have a live run
    if db and req.job_run_id and req.status in (SyntheticStatus.RUNNING, SyntheticStatus.QUEUED):
        try:
            run = db.jobs.get_run(run_id=int(req.job_run_id))
            life = run.state.life_cycle_state.value if run.state else None
            result = run.state.result_state.value   if run.state and run.state.result_state else None

            if life == "TERMINATED":
                req.status = SyntheticStatus.COMPLETE if result == "SUCCESS" else SyntheticStatus.FAILED
            elif life in ("RUNNING", "PENDING"):
                req.status = SyntheticStatus.RUNNING
        except Exception:
            pass  # Leave status unchanged on API error

    return req


@router.patch("/requests/{request_id}/cancel", response_model=SyntheticRequest)
def cancel_synthetic_request(request_id: str):
    """Cancel a queued synthetic request."""
    req = _REQUESTS.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Synthetic request '{request_id}' not found.")
    if req.status not in (SyntheticStatus.QUEUED,):
        raise HTTPException(status_code=409, detail=f"Cannot cancel request in status '{req.status}'.")
    req.status = SyntheticStatus.FAILED
    return req
