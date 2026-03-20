# TDM Deckers

Enterprise **Test Data Management (TDM)** platform for retail, built on **Databricks + AWS**.
Provides masked production-like data, synthetic data generation, domain subsetting, and a full
request-approval workflow — with a React UI and a FastAPI backend.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  React / Next.js frontend  (frontend/)                               │
│  • 7 pages: login, dashboard, catalog, requests, jobs, lineage, admin│
│  • openapi-fetch typed client ← generated from FastAPI OpenAPI spec  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  HTTP (localhost:8000 / prod URL)
┌────────────────────────────▼─────────────────────────────────────────┐
│  FastAPI backend  (backend/)                                         │
│  Routers: /domains  /datasets  /requests  /jobs  /masking  /lineage  │
│           /synthetic                                                  │
│  Connectors: Databricks SDK (optional) · boto3 S3                    │
└────────────┬───────────────────────────────────────────────────────┬─┘
             │ Databricks SDK                                         │ boto3
┌────────────▼──────────────────┐            ┌───────────────────────▼──┐
│  Databricks workspace          │            │  AWS S3                   │
│  • Unity Catalog (tdm_catalog) │            │  tdm-deckers-staged-dev/  │
│  • Delta Bronze / Silver tables│            │  raw/, synthetic/         │
│  • PySpark pipeline (DAB)      │            └──────────────────────────┘
│    ingest → mask → transform   │
│    databricks/ (bundles, src)  │
└───────────────────────────────┘
```

### Pipeline layers

| Layer | Location | Description |
|---|---|---|
| **Raw** | `s3://tdm-deckers-staged-dev/raw/{domain}/` | Source CSV files |
| **Bronze** | `tdm_catalog.tdm_dev.bronze_{domain}` | Ingested Delta tables |
| **Silver** | `tdm_catalog.tdm_dev.silver_{domain}` | Masked + transformed |
| **Synthetic** | `s3://tdm-deckers-staged-dev/synthetic/` | Generated fake data |

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | ≥ 3.10 | With `pip` |
| Node.js | ≥ 18 | With `npm` |
| Databricks CLI | ≥ 0.200 | `pip install databricks-cli` |
| AWS CLI | ≥ 2 | For S3 access |
| PySpark | ≥ 3.5 | `pip install pyspark` (for local tests) |

---

## Quick Start (3 commands)

```bash
# 1. Clone and enter repo
git clone https://github.com/pratikpdp99-lab/aws-adb-git.git
cd aws-adb-git

# 2. Install everything
make install

# 3. Start backend + frontend
cp .env.example .env          # fill in credentials (see below)
make dev
```

- **Frontend**: http://localhost:3000  — sign in with `alice@deckers.com` / `admin123`
- **Backend API**: http://localhost:8000
- **API docs (Swagger)**: http://localhost:8000/docs
- **API docs (ReDoc)**: http://localhost:8000/redoc

> **No backend?** The frontend works standalone — it falls back to mock data automatically.

---

## Detailed Setup

### 1. Backend

```bash
pip install -r backend/requirements.txt
```

Create `.env` from the template:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Databricks (optional — endpoints degrade gracefully without it)
DATABRICKS_HOST=https://dbc-xxxxxxxx-xxxx.cloud.databricks.com
DATABRICKS_TOKEN=dapixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# AWS (optional — uses ~/.aws/credentials if not set)
AWS_REGION=us-east-1
TDM_S3_BUCKET=tdm-deckers-staged-dev

# Unity Catalog
TDM_CATALOG=tdm_catalog
TDM_SCHEMA_DEV=tdm_dev

# Databricks job IDs (set after deploying the DAB bundle)
TDM_INGEST_JOB_ID=
TDM_PIPELINE_JOB_ID=
```

**Verify connections:**
```bash
python backend/app/connection.py
```

**Run backend:**
```bash
make backend
# or: uvicorn backend.app.main:app --reload --port 8000
```

**Run backend tests:**
```bash
make test-backend
# 39 tests, ~1.5 s
```

---

### 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local` (optional — defaults to `http://localhost:8000`):
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Run frontend:**
```bash
make frontend
# or: cd frontend && npm run dev
```

**Production build:**
```bash
make build
```

**Demo accounts** (no backend required):

| Email | Password | Role |
|---|---|---|
| alice@deckers.com | admin123 | Admin |
| bob@deckers.com | engineer123 | Engineer |
| carol@deckers.com | analyst123 | Analyst |

---

### 3. Databricks pipeline

**Local tests** (no Databricks needed — uses PySpark in local mode):

```bash
make test-databricks
# 22 tests covering ingest, mask, transform, quality, catalog
```

**Deploy to Databricks** (requires workspace credentials in `.env`):

```bash
# Install the Databricks CLI
pip install databricks-cli
databricks configure --token      # paste host + token

# Deploy the Asset Bundle
make bundle-deploy-dev
# or: cd databricks && databricks bundle deploy --target dev
```

The DAB bundle (`databricks/bundles/databricks.yml`) creates:
- A **4-task job**: ingest_customer → ingest_order → ingest_product → register_catalog
- A **daily schedule** at 06:00 UTC
- Separate targets: `dev`, `staging`, `prod`

**Run pipeline manually:**
```bash
databricks bundle run tdm-full-pipeline --target dev
```

---

### 4. AWS infrastructure (optional)

```bash
cd infra/aws
terraform init
make tf-plan        # preview
terraform apply -var="env=dev"
```

Creates:
- S3 bucket `tdm-deckers-staged-dev` with versioning + SSE-S3 encryption
- IAM policy allowing Databricks to read/write the bucket

---

## OpenAPI Client

The frontend uses a **fully typed API client** generated from the FastAPI OpenAPI schema.

**Regenerate after backend changes:**

```bash
make generate-client
# or: bash scripts/generate_client.sh
```

This runs two steps:
1. `python scripts/export_openapi.py` → `frontend/openapi.json`
2. `cd frontend && npm run generate-client` → `frontend/src/lib/api-types.ts`

Both generated files are committed to the repo so the frontend can be built
without a running backend.

**How the client works:**

```typescript
// frontend/src/lib/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./api-types";   // ← generated

export const api = createClient<paths>({ baseUrl: BASE_URL });

// Usage — fully typed, no try/catch needed:
const { data, error } = await api.GET("/domains/");
const { data, error } = await api.POST("/requests/", { body: { ... } });
```

Every request parameter and response shape is checked at compile time against
the backend contract.

---

## Repository Structure

```
aws-adb-git/
│
├── backend/                    FastAPI service
│   ├── app/
│   │   ├── main.py             Mounts all routers
│   │   ├── config.py           pydantic-settings (reads .env)
│   │   ├── connectors.py       Databricks + AWS dependency injection
│   │   ├── models.py           Pydantic request/response models
│   │   └── routers/
│   │       ├── health.py       GET /health
│   │       ├── datasets.py     GET /datasets/
│   │       ├── requests.py     POST/GET/PATCH /requests/
│   │       ├── domains.py      GET /domains/
│   │       ├── masking.py      CRUD /masking/policies
│   │       ├── synthetic.py    POST/GET /synthetic/requests
│   │       ├── jobs.py         GET/POST /jobs/
│   │       └── lineage.py      GET /lineage/{domain}
│   ├── tests/                  39 pytest tests
│   └── requirements.txt
│
├── databricks/                 PySpark pipeline
│   ├── bundles/
│   │   └── databricks.yml      DAB config (jobs, clusters, targets)
│   ├── src/
│   │   ├── pipeline.py         Orchestrator (run_pipeline)
│   │   ├── ingest.py           S3 CSV → Bronze Delta
│   │   ├── transform.py        Bronze → Silver (mask + transforms)
│   │   ├── quality.py          DQ checks (completeness, uniqueness, validity)
│   │   ├── catalog.py          Unity Catalog registration + PII tagging
│   │   ├── mask.py             SHA-256 tokenisation UDF
│   │   └── utils.py            Helpers (table_name with catalog/no-catalog)
│   ├── sample_data/            customer/order/product CSVs (10 rows each)
│   └── tests/                  22 PySpark local-mode tests
│
├── frontend/                   Next.js 14 + Tailwind CSS
│   ├── openapi.json            FastAPI schema (auto-generated, committed)
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api-types.ts    TypeScript types (auto-generated, committed)
│   │   │   ├── client.ts       openapi-fetch typed client
│   │   │   ├── api.ts          High-level functions with mock fallback
│   │   │   └── mock.ts         Mock data for offline dev
│   │   ├── types/index.ts      Shared TypeScript interfaces
│   │   ├── components/         Layout, Badge, StatCard, LineageGraph
│   │   └── pages/
│   │       ├── login.tsx       Login with demo accounts
│   │       ├── index.tsx       Dashboard
│   │       ├── catalog.tsx     Data domain catalog
│   │       ├── requests.tsx    4-step request wizard + history table
│   │       ├── jobs.tsx        Databricks job run monitor
│   │       ├── lineage.tsx     S3→Bronze→Silver lineage graph
│   │       └── admin.tsx       Masking policy management (admin only)
│   └── package.json
│
├── infra/
│   ├── aws/                    Terraform: S3 bucket + IAM
│   └── databricks/             Terraform: workspace stubs
│
├── scripts/
│   ├── export_openapi.py       Export FastAPI schema → openapi.json
│   ├── generate_client.sh      Full regeneration pipeline
│   └── dev.sh                  Start backend + frontend
│
├── Makefile                    Convenience targets (make help)
├── .env.example                Environment template
└── conftest.py                 Adds repo root to sys.path for tests
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/domains/` | List all retail domains |
| GET | `/domains/{name}` | Domain schema + PII fields |
| GET | `/datasets/` | List provisioned datasets |
| POST | `/requests/` | Submit test data request |
| GET | `/requests/` | List all requests |
| PATCH | `/requests/{id}/approve` | Approve a request |
| GET | `/jobs/` | List Databricks job runs |
| GET | `/jobs/{run_id}` | Get job run status |
| POST | `/jobs/trigger` | Trigger a job run |
| POST | `/masking/policies` | Create masking policy |
| GET | `/masking/policies` | List all policies |
| PUT | `/masking/policies/{domain}` | Update policy |
| DELETE | `/masking/policies/{domain}` | Delete policy |
| POST | `/synthetic/requests` | Submit synthetic data request |
| GET | `/lineage/{domain}` | Get pipeline lineage graph |

Full interactive docs at **http://localhost:8000/docs** when backend is running.

---

## Development Workflow

```bash
# 1. Make backend changes
# 2. Regenerate the TypeScript client
make generate-client

# 3. Run all tests
make test

# 4. Lint frontend
make lint

# 5. Commit
git add -A && git commit -m "feat: ..."
```

### Adding a new domain

1. Add to `SUPPORTED_DOMAINS` in `backend/app/models.py`
2. Add domain metadata to `backend/app/routers/domains.py`
3. Add Silver column list to `backend/app/routers/lineage.py`
4. Add sample CSV to `databricks/sample_data/`
5. Add domain transform in `databricks/src/transform.py`
6. Run `make generate-client` to update frontend types
7. Run `make test` to verify

### Adding a new API endpoint

1. Add Pydantic models to `backend/app/models.py`
2. Add router in `backend/app/routers/`
3. Mount in `backend/app/main.py`
4. Write tests in `backend/tests/`
5. Run `make generate-client` — new endpoint appears in the typed client

---

## Supported Environments

| Env | PII masking | Databricks scope |
|---|---|---|
| `dev` | Required for PII domains | `tdm_dev` schema |
| `staging` | Required | `tdm_staging` schema |
| `prod` | Full masking + admin approval | `tdm_prod` schema |

---

## Connections

| Service | How configured |
|---|---|
| Databricks | `DATABRICKS_HOST` + `DATABRICKS_TOKEN` in `.env` |
| AWS S3 | `~/.aws/credentials` (IAM user `claude-adb-tdm-git`) or env vars |
| Unity Catalog | Workspace URL + token — same as Databricks |

Verify all connections:
```bash
python backend/app/connection.py
```
