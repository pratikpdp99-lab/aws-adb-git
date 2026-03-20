// ── Auth ───────────────────────────────────────────────────────────────────────
export interface User {
  name: string;
  email: string;
  role: "admin" | "engineer" | "analyst";
}

// ── Domains ────────────────────────────────────────────────────────────────────
export interface DomainField {
  name: string;
  type: string;
  pii: boolean;
  nullable: boolean;
}

export interface Domain {
  name: string;
  description: string;
  fields: DomainField[];
  pii_fields: string[];
  supported_environments: string[];
  estimated_row_count: number;
}

// ── Datasets ───────────────────────────────────────────────────────────────────
export interface Dataset {
  id: string;
  name: string;
  domain: string;
  environment: string;
  row_count: number;
  masking_applied: boolean;
  created_at?: string;
}

// ── Data Requests ──────────────────────────────────────────────────────────────
export type RequestStatus = "PENDING" | "APPROVED" | "REJECTED" | "FULFILLED";

export interface DataRequest {
  id: string;
  domain: string;
  environment: string;
  row_count: number;
  status: RequestStatus;
  requester: string;
  purpose?: string;
  created_at: string;
  dataset_id?: string;
}

// ── Jobs ───────────────────────────────────────────────────────────────────────
export type JobStatus = "PENDING" | "RUNNING" | "SUCCESS" | "FAILED" | "SKIPPED";
export type JobTrigger = "MANUAL" | "SCHEDULE" | "API";

export interface JobRun {
  run_id: string;
  job_id: string;
  job_name: string;
  status: JobStatus;
  trigger: JobTrigger;
  start_time?: string;
  end_time?: string;
  error_message?: string;
  pipeline_run_id?: string;
}

// ── Masking ────────────────────────────────────────────────────────────────────
export type MaskingStrategy = "HASH" | "REDACT" | "NULLIFY" | "PARTIAL";

export interface FieldMaskingRule {
  field: string;
  strategy: MaskingStrategy;
}

export interface MaskingPolicy {
  id: string;
  domain: string;
  rules: FieldMaskingRule[];
  created_by: string;
  version: number;
  created_at: string;
}

// ── Synthetic ──────────────────────────────────────────────────────────────────
export type SyntheticStatus = "QUEUED" | "RUNNING" | "COMPLETE" | "FAILED";

export interface SyntheticRequest {
  id: string;
  domain: string;
  row_count: number;
  environment: string;
  locale?: string;
  seed?: number;
  requester?: string;
  status: SyntheticStatus;
  output_path?: string;
  job_run_id?: string;
  created_at: string;
}

// ── Lineage ────────────────────────────────────────────────────────────────────
export type LineageNodeType = "s3" | "bronze" | "silver";

export interface LineageNode {
  id: string;
  name: string;
  type: LineageNodeType;
  location?: string;
  catalog?: string;
  schema_name?: string;
}

export interface LineageEdge {
  from_node: string;
  to_node: string;
  transform: string;
}

export interface ColumnLineage {
  column: string;
  pii: boolean;
  masked: boolean;
  masking_strategy?: string;
  source_column: string;
}

export interface TableLineage {
  table: string;
  domain: string;
  nodes: LineageNode[];
  edges: LineageEdge[];
  columns: ColumnLineage[];
  pipeline_run_id?: string;
}
