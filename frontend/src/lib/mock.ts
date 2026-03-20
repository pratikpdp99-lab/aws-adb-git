/**
 * Mock data matching the backend API contracts.
 * Used as fallback when the API is unavailable or in local dev without a backend.
 */

import type {
  Domain, Dataset, DataRequest, JobRun, MaskingPolicy, TableLineage,
} from "../types";

export const MOCK_DOMAINS: Domain[] = [
  {
    name: "customer",
    description: "Retail customer master data including PII contact fields.",
    fields: [
      { name: "customer_id",  type: "string",  pii: false, nullable: false },
      { name: "first_name",   type: "string",  pii: true,  nullable: false },
      { name: "last_name",    type: "string",  pii: true,  nullable: false },
      { name: "email",        type: "string",  pii: true,  nullable: false },
      { name: "phone",        type: "string",  pii: true,  nullable: true  },
      { name: "ssn",          type: "string",  pii: true,  nullable: true  },
      { name: "address",      type: "string",  pii: true,  nullable: true  },
      { name: "created_date", type: "date",    pii: false, nullable: true  },
    ],
    pii_fields: ["first_name", "last_name", "email", "phone", "ssn", "address"],
    supported_environments: ["dev", "staging"],
    estimated_row_count: 500_000,
  },
  {
    name: "order",
    description: "Customer order transactions with fulfillment status.",
    fields: [
      { name: "order_id",          type: "string",  pii: false, nullable: false },
      { name: "customer_id",       type: "string",  pii: true,  nullable: false },
      { name: "order_date",        type: "date",    pii: false, nullable: false },
      { name: "total_amount",      type: "double",  pii: false, nullable: false },
      { name: "status",            type: "string",  pii: false, nullable: false },
      { name: "billing_address",   type: "string",  pii: true,  nullable: true  },
      { name: "shipping_address",  type: "string",  pii: true,  nullable: true  },
    ],
    pii_fields: ["customer_id", "billing_address", "shipping_address"],
    supported_environments: ["dev", "staging"],
    estimated_row_count: 2_000_000,
  },
  {
    name: "product",
    description: "Product catalog — no PII, safe for all environments.",
    fields: [
      { name: "product_id", type: "string",  pii: false, nullable: false },
      { name: "name",       type: "string",  pii: false, nullable: false },
      { name: "category",   type: "string",  pii: false, nullable: true  },
      { name: "price",      type: "double",  pii: false, nullable: false },
      { name: "in_stock",   type: "boolean", pii: false, nullable: false },
    ],
    pii_fields: [],
    supported_environments: ["dev", "staging", "prod"],
    estimated_row_count: 50_000,
  },
  {
    name: "inventory",
    description: "Store and warehouse inventory levels per product and location.",
    fields: [
      { name: "inventory_id", type: "string",    pii: false, nullable: false },
      { name: "product_id",   type: "string",    pii: false, nullable: false },
      { name: "location_id",  type: "string",    pii: false, nullable: false },
      { name: "quantity",     type: "integer",   pii: false, nullable: false },
      { name: "updated_at",   type: "timestamp", pii: false, nullable: true  },
    ],
    pii_fields: [],
    supported_environments: ["dev", "staging", "prod"],
    estimated_row_count: 200_000,
  },
  {
    name: "loyalty",
    description: "Customer loyalty programme — points, tiers, redemptions.",
    fields: [
      { name: "loyalty_id",    type: "string",  pii: false, nullable: false },
      { name: "customer_id",   type: "string",  pii: true,  nullable: false },
      { name: "email",         type: "string",  pii: true,  nullable: false },
      { name: "points",        type: "integer", pii: false, nullable: false },
      { name: "tier",          type: "string",  pii: false, nullable: false },
      { name: "enrolled_date", type: "date",    pii: false, nullable: true  },
    ],
    pii_fields: ["customer_id", "email"],
    supported_environments: ["dev", "staging"],
    estimated_row_count: 300_000,
  },
];

export const MOCK_DATASETS: Dataset[] = [
  { id: "DS-0001", name: "customer_dev_20240301",   domain: "customer",  environment: "dev",     row_count: 10000,  masking_applied: true,  created_at: "2024-03-01T06:12:34Z" },
  { id: "DS-0002", name: "order_dev_20240301",      domain: "order",     environment: "dev",     row_count: 25000,  masking_applied: true,  created_at: "2024-03-01T06:14:00Z" },
  { id: "DS-0003", name: "product_prod_20240302",   domain: "product",   environment: "prod",    row_count: 48500,  masking_applied: false, created_at: "2024-03-02T08:00:00Z" },
  { id: "DS-0004", name: "loyalty_staging_20240303",domain: "loyalty",   environment: "staging", row_count: 5000,   masking_applied: true,  created_at: "2024-03-03T09:30:00Z" },
  { id: "DS-0005", name: "inventory_dev_20240303",  domain: "inventory", environment: "dev",     row_count: 150000, masking_applied: false, created_at: "2024-03-03T10:00:00Z" },
];

export const MOCK_REQUESTS: DataRequest[] = [
  { id: "REQ-0001", domain: "customer",  environment: "dev",     row_count: 10000, status: "FULFILLED", requester: "alice@deckers.com", purpose: "Integration test suite",  created_at: "2024-03-01T05:00:00Z", dataset_id: "DS-0001" },
  { id: "REQ-0002", domain: "order",     environment: "dev",     row_count: 25000, status: "FULFILLED", requester: "bob@deckers.com",   purpose: "Performance benchmarking", created_at: "2024-03-01T05:10:00Z", dataset_id: "DS-0002" },
  { id: "REQ-0003", domain: "loyalty",   environment: "staging", row_count: 5000,  status: "APPROVED",  requester: "carol@deckers.com", purpose: "UAT campaign flow",        created_at: "2024-03-03T09:00:00Z" },
  { id: "REQ-0004", domain: "product",   environment: "prod",    row_count: 50000, status: "PENDING",   requester: "dave@deckers.com",  purpose: "Prod smoke test",          created_at: "2024-03-04T11:00:00Z" },
  { id: "REQ-0005", domain: "inventory", environment: "dev",     row_count: 2000,  status: "REJECTED",  requester: "eve@deckers.com",   purpose: "Data exploration",         created_at: "2024-03-04T12:00:00Z" },
];

export const MOCK_JOBS: JobRun[] = [
  { run_id: "1001", job_id: "stub-001", job_name: "tdm-full-pipeline-dev",     status: "SUCCESS", trigger: "SCHEDULE", start_time: "2024-03-01T06:00:00Z", end_time: "2024-03-01T06:12:34Z", pipeline_run_id: "abc-001" },
  { run_id: "1002", job_id: "stub-001", job_name: "tdm-full-pipeline-dev",     status: "SUCCESS", trigger: "MANUAL",   start_time: "2024-03-02T06:00:00Z", end_time: "2024-03-02T06:09:11Z", pipeline_run_id: "abc-002" },
  { run_id: "1003", job_id: "stub-002", job_name: "tdm-ingest-customer",       status: "FAILED",  trigger: "API",      start_time: "2024-03-03T08:00:00Z", end_time: "2024-03-03T08:02:05Z", error_message: "S3 source file not found" },
  { run_id: "1004", job_id: "stub-001", job_name: "tdm-full-pipeline-staging", status: "RUNNING", trigger: "SCHEDULE", start_time: "2024-03-04T06:00:00Z" },
  { run_id: "1005", job_id: "stub-003", job_name: "tdm-synthetic-order",       status: "SUCCESS", trigger: "API",      start_time: "2024-03-04T09:00:00Z", end_time: "2024-03-04T09:05:20Z" },
  { run_id: "1006", job_id: "stub-001", job_name: "tdm-full-pipeline-dev",     status: "PENDING", trigger: "SCHEDULE", start_time: "2024-03-05T06:00:00Z" },
];

export const MOCK_POLICIES: MaskingPolicy[] = [
  {
    id: "POL-0001", domain: "customer", version: 3, created_by: "admin@deckers.com", created_at: "2024-03-04T08:00:00Z",
    rules: [
      { field: "first_name", strategy: "REDACT" },
      { field: "last_name",  strategy: "REDACT" },
      { field: "email",      strategy: "HASH"   },
      { field: "phone",      strategy: "PARTIAL"},
      { field: "ssn",        strategy: "NULLIFY"},
      { field: "address",    strategy: "REDACT" },
    ],
  },
  {
    id: "POL-0002", domain: "order", version: 1, created_by: "admin@deckers.com", created_at: "2024-03-01T08:00:00Z",
    rules: [
      { field: "customer_id",      strategy: "HASH"  },
      { field: "billing_address",  strategy: "REDACT"},
      { field: "shipping_address", strategy: "REDACT"},
    ],
  },
  {
    id: "POL-0003", domain: "loyalty", version: 2, created_by: "policy-bot@deckers.com", created_at: "2024-03-02T10:00:00Z",
    rules: [
      { field: "customer_id", strategy: "HASH"  },
      { field: "email",       strategy: "HASH"  },
    ],
  },
];

export const MOCK_LINEAGE: Record<string, TableLineage> = {
  customer: {
    table: "silver_customer", domain: "customer",
    nodes: [
      { id: "s3-customer",     name: "s3://tdm-deckers-staged-dev/raw/customer/", type: "s3",     location: "s3://tdm-deckers-staged-dev/raw/customer/" },
      { id: "bronze-customer", name: "bronze_customer", type: "bronze", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.bronze_customer" },
      { id: "silver-customer", name: "silver_customer", type: "silver", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.silver_customer" },
    ],
    edges: [
      { from_node: "s3-customer",     to_node: "bronze-customer", transform: "ingest"          },
      { from_node: "bronze-customer", to_node: "silver-customer", transform: "mask+transform"  },
    ],
    columns: [
      { column: "customer_id",  pii: false, masked: false, source_column: "customer_id"  },
      { column: "given_name",   pii: true,  masked: true,  masking_strategy: "REDACT", source_column: "first_name"  },
      { column: "family_name",  pii: true,  masked: true,  masking_strategy: "REDACT", source_column: "last_name"   },
      { column: "email",        pii: true,  masked: true,  masking_strategy: "HASH",   source_column: "email"       },
      { column: "phone",        pii: true,  masked: true,  masking_strategy: "PARTIAL",source_column: "phone"       },
      { column: "ssn",          pii: true,  masked: true,  masking_strategy: "NULLIFY",source_column: "ssn"         },
      { column: "address",      pii: true,  masked: true,  masking_strategy: "REDACT", source_column: "address"     },
      { column: "created_date", pii: false, masked: false, source_column: "created_date" },
      { column: "email_domain", pii: false, masked: false, source_column: "email_domain" },
      { column: "_tdm_pipeline_run_id",  pii: false, masked: false, source_column: "_tdm_pipeline_run_id"  },
      { column: "_tdm_masking_applied",  pii: false, masked: false, source_column: "_tdm_masking_applied"  },
      { column: "_tdm_ingested_at",      pii: false, masked: false, source_column: "_tdm_ingested_at"      },
    ],
  },
  order: {
    table: "silver_order", domain: "order",
    nodes: [
      { id: "s3-order",     name: "s3://tdm-deckers-staged-dev/raw/order/", type: "s3",     location: "s3://tdm-deckers-staged-dev/raw/order/" },
      { id: "bronze-order", name: "bronze_order", type: "bronze", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.bronze_order" },
      { id: "silver-order", name: "silver_order", type: "silver", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.silver_order" },
    ],
    edges: [
      { from_node: "s3-order",     to_node: "bronze-order", transform: "ingest"         },
      { from_node: "bronze-order", to_node: "silver-order", transform: "mask+transform" },
    ],
    columns: [
      { column: "order_id",         pii: false, masked: false, source_column: "order_id"        },
      { column: "customer_id",      pii: true,  masked: true,  masking_strategy: "HASH",   source_column: "customer_id"     },
      { column: "order_date",       pii: false, masked: false, source_column: "order_date"      },
      { column: "total_amount",     pii: false, masked: false, source_column: "total_amount"    },
      { column: "status",           pii: false, masked: false, source_column: "status"          },
      { column: "billing_address",  pii: true,  masked: true,  masking_strategy: "REDACT", source_column: "billing_address" },
      { column: "shipping_address", pii: true,  masked: true,  masking_strategy: "REDACT", source_column: "shipping_address"},
      { column: "_tdm_ingested_at", pii: false, masked: false, source_column: "_tdm_ingested_at"},
    ],
  },
  product: {
    table: "silver_product", domain: "product",
    nodes: [
      { id: "s3-product",     name: "s3://tdm-deckers-staged-dev/raw/product/", type: "s3",     location: "s3://tdm-deckers-staged-dev/raw/product/" },
      { id: "bronze-product", name: "bronze_product", type: "bronze", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.bronze_product" },
      { id: "silver-product", name: "silver_product", type: "silver", catalog: "tdm_catalog", schema_name: "tdm_dev", location: "tdm_catalog.tdm_dev.silver_product" },
    ],
    edges: [
      { from_node: "s3-product",     to_node: "bronze-product", transform: "ingest"         },
      { from_node: "bronze-product", to_node: "silver-product", transform: "mask+transform" },
    ],
    columns: [
      { column: "product_id", pii: false, masked: false, source_column: "product_id" },
      { column: "name",       pii: false, masked: false, source_column: "name"       },
      { column: "category",   pii: false, masked: false, source_column: "category"   },
      { column: "price",      pii: false, masked: false, source_column: "price"      },
      { column: "in_stock",   pii: false, masked: false, source_column: "in_stock"   },
      { column: "name_upper", pii: false, masked: false, source_column: "name"       },
      { column: "_tdm_ingested_at", pii: false, masked: false, source_column: "_tdm_ingested_at" },
    ],
  },
};
