"""
Test data request endpoints — submit, approve, and track data requests.
"""

from fastapi import APIRouter, HTTPException
from backend.app.models import DataRequest, DataRequestCreate, DataRequestStatus

router = APIRouter()

# Stub in-memory store — replace with DB
_REQUESTS: dict[str, DataRequest] = {}
_counter = 1


@router.post("/", response_model=DataRequest, status_code=201)
def create_request(body: DataRequestCreate):
    """Submit a new test data request."""
    global _counter
    req_id = f"REQ-{_counter:04d}"
    _counter += 1
    req = DataRequest(
        id=req_id,
        requester=body.requester,
        domain=body.domain,
        environment=body.environment,
        row_count=body.row_count,
        status=DataRequestStatus.PENDING,
    )
    _REQUESTS[req_id] = req
    return req


@router.get("/", response_model=list[DataRequest])
def list_requests(status: DataRequestStatus = None):
    """List all requests, optionally filtered by status."""
    results = list(_REQUESTS.values())
    if status:
        results = [r for r in results if r.status == status]
    return results


@router.get("/{request_id}", response_model=DataRequest)
def get_request(request_id: str):
    req = _REQUESTS.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Request '{request_id}' not found")
    return req


@router.patch("/{request_id}/approve", response_model=DataRequest)
def approve_request(request_id: str):
    """Approve a pending request."""
    req = _REQUESTS.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Request '{request_id}' not found")
    req.status = DataRequestStatus.APPROVED
    return req
