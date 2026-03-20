"""Pydantic models for TDM API."""

from enum import Enum
from pydantic import BaseModel


# ── Datasets ─────────────────────────────────────────────────────────────────

class Dataset(BaseModel):
    id: str
    name: str
    domain: str          # customer | order | product | inventory | loyalty
    environment: str     # dev | staging | prod
    row_count: int
    masking_applied: bool


class DatasetList(BaseModel):
    datasets: list[Dataset]
    total: int


# ── Requests ─────────────────────────────────────────────────────────────────

class DataRequestStatus(str, Enum):
    PENDING  = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FULFILLED = "FULFILLED"


class DataRequestCreate(BaseModel):
    requester: str
    domain: str
    environment: str
    row_count: int


class DataRequest(DataRequestCreate):
    id: str
    status: DataRequestStatus
