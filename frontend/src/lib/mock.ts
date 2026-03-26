/**
 * Mock data matching the backend API contracts.
 * Used as fallback when the API is unavailable or in local dev without a backend.
 */

import type {
  Domain, Dataset, DataRequest, JobRun, MaskingPolicy, TableLineage,
  DeckersProduct, RecommendResult,
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

// ── Deckers D2C Product Catalog (mock) ─────────────────────────────────────────
export const MOCK_PRODUCTS: DeckersProduct[] = [
  {
    product_id: "UGG-001", brand: "UGG", name: "Classic Short II Boot", category: "boots",
    price: 160, msrp: 160, rating: 4.8, review_count: 48320, in_stock: true, colors_available: 12,
    features: ["Genuine suede upper", "UGGplush™ wool blend lining", "Treadlite by UGG™ outsole", "Water-resistant treatment"],
    use_cases: ["comfort", "casual", "cold-weather"],
    best_for: ["everyday wear", "cold climates", "gifting"],
    seasons: ["fall", "winter"], gender: "women", sustainability_score: 55, d2c_exclusive: false,
    return_rate_pct: 6.2, channel: "D2C",
  },
  {
    product_id: "UGG-002", brand: "UGG", name: "Tasman Slipper", category: "slippers",
    price: 120, msrp: 120, rating: 4.7, review_count: 62100, in_stock: true, colors_available: 18,
    features: ["Sheepskin collar", "Suede heel counter", "UGGpure™ wool sockliner", "Flexible EVA outsole"],
    use_cases: ["comfort", "casual", "indoor-outdoor"],
    best_for: ["gifting", "everyday casual", "year-round comfort"],
    seasons: ["spring", "fall", "winter", "summer"], gender: "unisex", sustainability_score: 58, d2c_exclusive: false,
    return_rate_pct: 4.8, channel: "D2C",
  },
  {
    product_id: "UGG-003", brand: "UGG", name: "Neumel Boot", category: "boots",
    price: 150, msrp: 150, rating: 4.6, review_count: 28450, in_stock: true, colors_available: 8,
    features: ["Nubuck upper", "UGGpure™ wool lining", "Crepe rubber outsole", "Chukka silhouette"],
    use_cases: ["comfort", "casual", "cold-weather"],
    best_for: ["men's gifting", "casual office", "weekend wear"],
    seasons: ["fall", "winter"], gender: "men", sustainability_score: 53, d2c_exclusive: false,
    return_rate_pct: 7.1, channel: "D2C",
  },
  {
    product_id: "UGG-004", brand: "UGG", name: "Ultra Mini Platform Boot", category: "boots",
    price: 170, msrp: 170, rating: 4.5, review_count: 15200, in_stock: true, colors_available: 10,
    features: ["Genuine suede", "UGGplush™ lining", "Platform EVA outsole", "D2C-exclusive colorways"],
    use_cases: ["fashion", "casual", "cold-weather"],
    best_for: ["fashion-forward", "holiday gifting", "street style"],
    seasons: ["fall", "winter"], gender: "women", sustainability_score: 52, d2c_exclusive: true,
    return_rate_pct: 8.4, channel: "D2C",
  },
  {
    product_id: "UGG-005", brand: "UGG", name: "Scuffette II Slipper", category: "slippers",
    price: 95, msrp: 95, rating: 4.6, review_count: 38600, in_stock: true, colors_available: 14,
    features: ["Sheepskin upper", "UGGpure™ wool lining", "Flexible outsole", "Slip-on silhouette"],
    use_cases: ["comfort", "indoor-outdoor"],
    best_for: ["everyday comfort", "gifting", "recovery"],
    seasons: ["spring", "fall", "winter", "summer"], gender: "women", sustainability_score: 56, d2c_exclusive: false,
    return_rate_pct: 5.0, channel: "D2C",
  },
  {
    product_id: "HOK-001", brand: "HOKA", name: "Clifton 9", category: "road_running",
    price: 145, msrp: 145, rating: 4.7, review_count: 24300, in_stock: true, colors_available: 20,
    features: ["CMEVA midsole", "Early-stage meta-rocker", "Engineered mesh upper", "Full-length compression-molded EVA"],
    use_cases: ["running", "road-running", "daily-training", "walking"],
    best_for: ["daily mileage", "marathon training", "recovery runs"],
    seasons: ["spring", "summer", "fall"], gender: "unisex", sustainability_score: 62, d2c_exclusive: false,
    return_rate_pct: 5.5, channel: "D2C",
  },
  {
    product_id: "HOK-002", brand: "HOKA", name: "Speedgoat 5", category: "trail",
    price: 155, msrp: 155, rating: 4.8, review_count: 18900, in_stock: true, colors_available: 15,
    features: ["Vibram® Megagrip outsole", "Max cushion midsole", "Reinforced toe cap", "Quick-Dry mesh upper"],
    use_cases: ["trail-running", "hiking", "outdoor", "running"],
    best_for: ["technical trails", "ultra events", "rugged terrain"],
    seasons: ["spring", "summer", "fall"], gender: "unisex", sustainability_score: 60, d2c_exclusive: false,
    return_rate_pct: 4.2, channel: "D2C",
  },
  {
    product_id: "HOK-003", brand: "HOKA", name: "Bondi 8", category: "road_running",
    price: 165, msrp: 165, rating: 4.6, review_count: 31200, in_stock: true, colors_available: 22,
    features: ["Maximum EVA cushion", "Meta-Rocker geometry", "Plush collar and tongue", "Extended heel crash pad"],
    use_cases: ["running", "road-running", "walking", "comfort"],
    best_for: ["maximum cushion seekers", "long-distance", "standing all day"],
    seasons: ["spring", "summer", "fall", "winter"], gender: "unisex", sustainability_score: 63, d2c_exclusive: false,
    return_rate_pct: 6.0, channel: "D2C",
  },
  {
    product_id: "HOK-004", brand: "HOKA", name: "Challenger ATR 7", category: "trail",
    price: 135, msrp: 135, rating: 4.5, review_count: 12400, in_stock: true, colors_available: 12,
    features: ["Multi-directional lugs", "Lightweight EVA midsole", "Breathable mesh", "All-terrain-ready outsole"],
    use_cases: ["trail-running", "hiking", "outdoor", "running"],
    best_for: ["trail-to-road transitions", "beginner trail runners"],
    seasons: ["spring", "summer", "fall"], gender: "unisex", sustainability_score: 58, d2c_exclusive: false,
    return_rate_pct: 5.8, channel: "D2C",
  },
  {
    product_id: "HOK-005", brand: "HOKA", name: "Rincon 3", category: "road_running",
    price: 130, msrp: 130, rating: 4.5, review_count: 16800, in_stock: true, colors_available: 16,
    features: ["Lightweight EVA foam", "Breathable mesh upper", "Early-stage meta-rocker", "Single-layer construction"],
    use_cases: ["running", "road-running", "speed-training"],
    best_for: ["tempo runs", "racing", "lightweight preference"],
    seasons: ["spring", "summer", "fall"], gender: "unisex", sustainability_score: 59, d2c_exclusive: false,
    return_rate_pct: 5.2, channel: "D2C",
  },
  {
    product_id: "TEV-001", brand: "Teva", name: "Original Universal Sandal", category: "sandals",
    price: 50, msrp: 50, rating: 4.6, review_count: 45200, in_stock: true, colors_available: 24,
    features: ["Strappy nylon upper", "Hook-and-loop closure", "EVA foam midsole", "Spider Original rubber outsole"],
    use_cases: ["outdoor", "casual", "water", "hiking-light"],
    best_for: ["beach", "camping", "travel", "everyday summer"],
    seasons: ["spring", "summer"], gender: "unisex", sustainability_score: 72, d2c_exclusive: false,
    return_rate_pct: 3.8, channel: "D2C",
  },
  {
    product_id: "TEV-002", brand: "Teva", name: "Hurricane XLT2", category: "sandals",
    price: 65, msrp: 65, rating: 4.5, review_count: 22100, in_stock: true, colors_available: 18,
    features: ["Quick-dry webbing", "Shoc Pad™ heel cushion", "Universal Strapping System", "High-traction rubber outsole"],
    use_cases: ["outdoor", "hiking", "water", "casual"],
    best_for: ["river crossings", "light hikes", "festival wear"],
    seasons: ["spring", "summer"], gender: "unisex", sustainability_score: 70, d2c_exclusive: false,
    return_rate_pct: 4.5, channel: "D2C",
  },
  {
    product_id: "TEV-003", brand: "Teva", name: "Terra Fi 5", category: "hiking",
    price: 100, msrp: 100, rating: 4.4, review_count: 9800, in_stock: true, colors_available: 8,
    features: ["Durabrasion rubber outsole", "Recycled webbing upper", "4mm lug depth", "Teva Float foam midsole"],
    use_cases: ["hiking", "outdoor", "water", "backpacking"],
    best_for: ["technical hikes", "canyoneering", "multi-day"],
    seasons: ["spring", "summer"], gender: "unisex", sustainability_score: 78, d2c_exclusive: false,
    return_rate_pct: 5.1, channel: "D2C",
  },
  {
    product_id: "SAN-001", brand: "Sanuk", name: "Yoga Mat 3 Sandal", category: "casual",
    price: 45, msrp: 45, rating: 4.4, review_count: 18200, in_stock: true, colors_available: 20,
    features: ["Real yoga mat footbed", "Vegan upper", "Lightweight EVA outsole", "Soft webbing straps"],
    use_cases: ["casual", "comfort", "indoor-outdoor"],
    best_for: ["yoga enthusiasts", "beach days", "casual daily"],
    seasons: ["spring", "summer"], gender: "women", sustainability_score: 68, d2c_exclusive: false,
    return_rate_pct: 4.2, channel: "D2C",
  },
  {
    product_id: "SAN-002", brand: "Sanuk", name: "Vagabond Canvas Sneaker", category: "casual",
    price: 65, msrp: 65, rating: 4.3, review_count: 12500, in_stock: true, colors_available: 10,
    features: ["Canvas upper", "Happy U™ construction", "Life is Good™ insole", "Flexible rubber outsole"],
    use_cases: ["casual", "comfort", "everyday"],
    best_for: ["laid-back lifestyle", "weekend casual", "travel"],
    seasons: ["spring", "summer", "fall"], gender: "men", sustainability_score: 65, d2c_exclusive: false,
    return_rate_pct: 6.0, channel: "D2C",
  },
  {
    product_id: "KOO-001", brand: "Koolaburra", name: "Victoria Short Boot", category: "boots",
    price: 90, msrp: 90, rating: 4.4, review_count: 8400, in_stock: true, colors_available: 9,
    features: ["Faux fur lining", "Suede-like upper", "Flexible outsole", "Pull-on silhouette"],
    use_cases: ["comfort", "casual", "cold-weather"],
    best_for: ["value shoppers", "gift ideas", "casual winter"],
    seasons: ["fall", "winter"], gender: "women", sustainability_score: 48, d2c_exclusive: false,
    return_rate_pct: 8.0, channel: "D2C",
  },
  {
    product_id: "KOO-002", brand: "Koolaburra", name: "Koola Short Boot", category: "boots",
    price: 80, msrp: 80, rating: 4.3, review_count: 5200, in_stock: false, colors_available: 7,
    features: ["Faux fur collar", "Fabric upper", "Slip-on design", "Lightweight EVA outsole"],
    use_cases: ["comfort", "casual", "cold-weather"],
    best_for: ["budget-conscious", "casual winter", "kids and teens"],
    seasons: ["fall", "winter"], gender: "unisex", sustainability_score: 45, d2c_exclusive: false,
    return_rate_pct: 9.5, channel: "D2C",
  },
];

export const MOCK_RECOMMEND_RESULT: RecommendResult = {
  based_on: undefined,
  context_summary: "Recommendations across full D2C catalog",
  recommendations: [
    { product: MOCK_PRODUCTS[6], score: 94.2, match_reasons: ["Top-rated (4.8★ from 18,900 reviews)", "Strong match for 'trail' activity", "High sustainability score (60/100)"] },
    { product: MOCK_PRODUCTS[5], score: 91.5, match_reasons: ["Top-rated (4.7★ from 24,300 reviews)", "Strong match for 'running' activity", "Available for all genders"] },
    { product: MOCK_PRODUCTS[7], score: 88.0, match_reasons: ["Highly rated (4.6★)", "Strong match for 'running' activity", "Maximum cushion platform"] },
    { product: MOCK_PRODUCTS[10], score: 85.3, match_reasons: ["Highly rated (4.6★)", "High sustainability score (72/100)", "Within budget"] },
    { product: MOCK_PRODUCTS[0], score: 82.1, match_reasons: ["Top-rated (4.8★ from 48,320 reviews)", "Perfect for fall", "Gifting favorite"] },
  ],
};
