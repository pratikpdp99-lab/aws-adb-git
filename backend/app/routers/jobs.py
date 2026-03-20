"""
Provisioning job endpoints.
Wraps the Databricks Jobs API to list, trigger, and monitor TDM pipeline runs.
Falls back to stub data when Databricks is not configured (local dev).
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState, RunResultState

from backend.app.models import JobRun, JobRunList, JobRunStatus, JobRunTrigger, JobTriggerRequest
from backend.app.config import Settings, get_settings
from backend.app.connectors import get_databricks, get_databricks_optional

router = APIRouter()


def _map_run_status(life: str, result: Optional[str]) -> JobRunStatus:
    if life in ("PENDING", "QUEUED"):
        return JobRunStatus.PENDING
    if life == "RUNNING":
        return JobRunStatus.RUNNING
    if life == "TERMINATED":
        return JobRunStatus.SUCCESS if result == "SUCCESS" else JobRunStatus.FAILED
    if life == "SKIPPED":
        return JobRunStatus.SKIPPED
    return JobRunStatus.PENDING


def _ms_to_iso(ms: Optional[int]) -> Optional[str]:
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


# ── Stub data (used when Databricks is not configured) ────────────────────────

_STUB_RUNS: list[JobRun] = [
    JobRun(
        run_id="1001",
        job_id="stub-001",
        job_name="tdm-full-pipeline-dev",
        status=JobRunStatus.SUCCESS,
        trigger=JobRunTrigger.MANUAL,
        start_time="2024-03-01T06:00:00+00:00",
        end_time="2024-03-01T06:12:34+00:00",
        pipeline_run_id="abc-123",
    ),
    JobRun(
        run_id="1002",
        job_id="stub-001",
        job_name="tdm-full-pipeline-dev",
        status=JobRunStatus.RUNNING,
        trigger=JobRunTrigger.SCHEDULE,
        start_time="2024-03-02T06:00:00+00:00",
    ),
]


@router.get("/", response_model=JobRunList)
def list_jobs(
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
    settings: Settings = Depends(get_settings),
    limit: int = 20,
):
    """List recent TDM provisioning job runs.
    Returns live data from Databricks when configured, stub data otherwise.
    """
    if not db:
        return JobRunList(runs=_STUB_RUNS, total=len(_STUB_RUNS))

    try:
        runs = []
        for run in db.jobs.list_runs(limit=limit):
            life   = run.state.life_cycle_state.value if run.state else "PENDING"
            result = run.state.result_state.value     if run.state and run.state.result_state else None
            runs.append(JobRun(
                run_id=str(run.run_id),
                job_id=str(run.job_id),
                job_name=run.run_name or f"job-{run.job_id}",
                status=_map_run_status(life, result),
                trigger=JobRunTrigger.API,
                start_time=_ms_to_iso(run.start_time),
                end_time=_ms_to_iso(run.end_time),
            ))
        return JobRunList(runs=runs, total=len(runs))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Databricks API error: {e}")


@router.get("/{run_id}", response_model=JobRun)
def get_job_run(
    run_id: str,
    db: Optional[WorkspaceClient] = Depends(get_databricks_optional),
):
    """Get status of a specific job run."""
    if not db:
        stub = next((r for r in _STUB_RUNS if r.run_id == run_id), None)
        if not stub:
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
        return stub

    try:
        run    = db.jobs.get_run(run_id=int(run_id))
        life   = run.state.life_cycle_state.value if run.state else "PENDING"
        result = run.state.result_state.value     if run.state and run.state.result_state else None
        return JobRun(
            run_id=str(run.run_id),
            job_id=str(run.job_id),
            job_name=run.run_name or f"job-{run.job_id}",
            status=_map_run_status(life, result),
            trigger=JobRunTrigger.API,
            start_time=_ms_to_iso(run.start_time),
            end_time=_ms_to_iso(run.end_time),
            error_message=run.state.state_message if run.state else None,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Databricks API error: {e}")


@router.post("/trigger", response_model=JobRun, status_code=202)
def trigger_job(
    body: JobTriggerRequest,
    db: WorkspaceClient = Depends(get_databricks),
    settings: Settings = Depends(get_settings),
):
    """Trigger a Databricks job run. Requires Databricks credentials."""
    try:
        run = db.jobs.run_now(
            job_id=int(body.job_id),
            job_parameters=body.params or {},
        )
        return JobRun(
            run_id=str(run.run_id),
            job_id=body.job_id,
            job_name=f"job-{body.job_id}",
            status=JobRunStatus.PENDING,
            trigger=JobRunTrigger.API,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to trigger job: {e}")


@router.post("/{run_id}/cancel", status_code=202)
def cancel_job_run(
    run_id: str,
    db: WorkspaceClient = Depends(get_databricks),
):
    """Cancel a running Databricks job run."""
    try:
        db.jobs.cancel_run(run_id=int(run_id))
        return {"message": f"Cancellation requested for run {run_id}"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to cancel run: {e}")
