"""Pydantic models for TDM API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Shared ────────────────────────────────────────────────────────────────────

SUPPORTED_DOMAINS = ["customer", "order", "product", "inventory", "loyalty"]
SUPPORTED_ENVS    = ["dev", "staging", "prod"]


# ── Datasets ──────────────────────────────────────────────────────────────────

class Dataset(BaseModel):
    id:               str
    name:             str
    domain:           str
    environment:      str
    row_count:        int
    masking_applied:  bool


class DatasetList(BaseModel):
    datasets: list[Dataset]
    total:    int


# ── Domains ───────────────────────────────────────────────────────────────────

class DomainField(BaseModel):
    name:     str
    type:     str
    pii:      bool = False
    nullable: bool = True


class Domain(BaseModel):
    name:                    str
    description:             str
    fields:                  list[DomainField]
    pii_fields:              list[str]
    supported_environments:  list[str]
    estimated_row_count:     int


class DomainList(BaseModel):
    domains: list[Domain]
    total:   int


# ── Test data requests ────────────────────────────────────────────────────────

class DataRequestStatus(str, Enum):
    PENDING   = "PENDING"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    FULFILLED = "FULFILLED"


class DataRequestCreate(BaseModel):
    requester:   str
    domain:      str
    environment: str
    row_count:   int
    purpose:     Optional[str] = None


class DataRequest(DataRequestCreate):
    id:         str
    status:     DataRequestStatus
    created_at: str = ""


# ── Masking policies ──────────────────────────────────────────────────────────

class MaskingStrategy(str, Enum):
    HASH    = "hash"
    REDACT  = "redact"
    NULLIFY = "nullify"
    PARTIAL = "partial"


class FieldMaskingRule(BaseModel):
    field:            str
    strategy:         MaskingStrategy
    preserve_format:  bool = False


class MaskingPolicyCreate(BaseModel):
    domain:     str
    rules:      list[FieldMaskingRule]
    created_by: str


class MaskingPolicy(MaskingPolicyCreate):
    id:         str
    version:    int
    created_at: str


# ── Synthetic data requests ───────────────────────────────────────────────────

class SyntheticStatus(str, Enum):
    QUEUED   = "QUEUED"
    RUNNING  = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED   = "FAILED"


class SyntheticRequestCreate(BaseModel):
    domain:      str
    row_count:   int
    environment: str
    locale:      str = "en_US"
    seed:        Optional[int] = None
    requester:   str


class SyntheticRequest(SyntheticRequestCreate):
    id:             str
    status:         SyntheticStatus
    output_path:    Optional[str] = None   # S3 URI when complete
    job_run_id:     Optional[str] = None   # Databricks run ID
    created_at:     str


# ── Provisioning jobs ─────────────────────────────────────────────────────────

class JobRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED  = "FAILED"
    SKIPPED = "SKIPPED"


class JobRunTrigger(str, Enum):
    MANUAL   = "manual"
    SCHEDULE = "schedule"
    API      = "api"


class JobRun(BaseModel):
    run_id:           str
    job_id:           str
    job_name:         str
    status:           JobRunStatus
    trigger:          JobRunTrigger
    start_time:       Optional[str] = None
    end_time:         Optional[str] = None
    pipeline_run_id:  Optional[str] = None
    error_message:    Optional[str] = None


class JobRunList(BaseModel):
    runs:  list[JobRun]
    total: int


class JobTriggerRequest(BaseModel):
    job_id:  str
    params:  dict = {}


# ── Lineage ───────────────────────────────────────────────────────────────────

class LineageNodeType(str, Enum):
    SOURCE = "source"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD   = "gold"
    S3     = "s3"


class LineageNode(BaseModel):
    id:          str
    name:        str
    type:        LineageNodeType
    catalog:     Optional[str] = None
    schema_name: Optional[str] = None
    location:    Optional[str] = None   # S3 URI or table path


class LineageEdge(BaseModel):
    from_node:  str
    to_node:    str
    transform:  str   # "ingest" | "mask" | "transform" | "subset"


class ColumnLineage(BaseModel):
    column:           str
    pii:              bool
    masked:           bool
    masking_strategy: Optional[str] = None
    source_column:    str


class TableLineage(BaseModel):
    table:           str
    domain:          str
    nodes:           list[LineageNode]
    edges:           list[LineageEdge]
    columns:         list[ColumnLineage]
    pipeline_run_id: Optional[str] = None
