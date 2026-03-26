# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project: TDM Platform — Deckers Brands

Enterprise Test Data Management platform for retail on Databricks + AWS.
Stack: FastAPI backend · Next.js + Streamlit frontends · Databricks/Delta/Unity Catalog · AWS S3/IAM.

---

## Repository Structure

```
aws-adb-git/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI entry point — mounts all routers
│   │   ├── models.py          All Pydantic models (DomainField has compliance_tags)
│   │   ├── config.py          Settings via pydantic-settings (@lru_cache)
│   │   ├── connectors.py      FastAPI dependency factories (Databricks, S3)
│   │   ├── agents/
│   │   │   ├── catalog_agent.py   Claude-powered catalog Q&A
│   │   │   └── dq_agent.py        DQ run summariser using Claude
│   │   └── routers/
│   │       ├── health.py          GET /health
│   │       ├── datasets.py        GET /datasets/
│   │       ├── domains.py         GET /domains/ (compliance_tags on DomainField)
│   │       ├── requests.py        POST/GET/PATCH /requests/
│   │       ├── masking.py         POST/GET/PUT/DELETE /masking/policies
│   │       ├── synthetic.py       POST/GET/PATCH /synthetic/requests
│   │       ├── jobs.py            GET/POST /jobs/ (source: live|stub field)
│   │       ├── lineage.py         GET /lineage/{domain}
│   │       ├── recommendations.py GET/POST /products/ (compare + recommend)
│   │       └── agents.py          POST /agents/catalog, POST /agents/dq
│   └── tests/
│       ├── conftest.py            Shared fixtures + autouse state reset
│       ├── test_datasets.py
│       ├── test_domains.py
│       ├── test_jobs.py
│       ├── test_masking.py
│       ├── test_requests.py
│       ├── test_synthetic.py
│       ├── test_recommendations.py
│       ├── test_guardrails.py     @guardrail PII leakage tests
│       └── test_compliance.py     @guardrail compliance tag tests
│
├── databricks/
│   ├── src/
│   │   ├── ingest.py          S3 → Bronze Delta
│   │   ├── mask.py            SHA-256 tokenisation + redaction (PII_FIELDS dict)
│   │   ├── transform.py       Bronze → Silver (domain transforms + lineage metadata)
│   │   ├── quality.py         DQ checks: CompletenessCheck, UniquenessCheck, ValidityCheck
│   │   ├── synthetic.py       Fake record generators (customer, order, payment)
│   │   ├── subset.py          Referential-integrity-preserving subsetting
│   │   ├── catalog.py         Unity Catalog registration
│   │   ├── pipeline.py        Full orchestrator (ingest→DQ→mask→transform→catalog)
│   │   └── utils.py           table_name() helper
│   └── tests/
│       ├── conftest.py            Shared local SparkSession fixture
│       ├── test_mask.py
│       ├── test_pipeline.py
│       ├── test_quality.py
│       ├── test_synthetic.py
│       ├── test_transform.py
│       └── test_guardrails.py     @guardrail PySpark PII guardrails
│
├── frontend/                  Next.js 14 + TypeScript + Tailwind (original frontend)
│   └── src/pages/             index, catalog, compare, jobs, lineage, requests, admin
│
├── frontend_py/               Streamlit Python dashboard
│   ├── app.py                 Entry point (auth check + sidebar)
│   ├── requirements.txt       streamlit, requests, pandas, plotly, anthropic
│   ├── .streamlit/config.toml Brand theme (indigo #4F46E5)
│   ├── lib/
│   │   ├── api_client.py      HTTP wrapper around FastAPI backend
│   │   ├── auth.py            Session-state login (demo accounts)
│   │   └── theme.py           Colour constants + STATUS_COLORS
│   └── pages/
│       ├── 1_Dashboard.py     KPI cards + recent jobs/requests
│       ├── 2_Data_Catalog.py  Domain schemas + PII badges + compliance tags
│       ├── 3_Jobs.py          Live job runs + auto-refresh (source indicator)
│       ├── 4_Requests.py      Submit + approve data requests
│       ├── 5_Compare.py       Deckers product comparator + recommendations
│       ├── 6_Security.py      IAM, connections, red-flag detection, compliance
│       ├── 7_E2E_Flow.py      Pipeline architecture explainer
│       └── 8_Agents.py        Catalog + DQ monitor agent chat UI
│
├── mcp_server/
│   ├── server.py              FastMCP server exposing TDM as MCP tools
│   └── requirements.txt       mcp[cli], httpx
│
├── infra/
│   ├── aws/                   Terraform: S3, IAM
│   └── databricks/            Terraform: workspace, Unity Catalog stubs
│
├── pytest.ini                 Test markers: unit, integration, databricks, guardrail
└── .claude/CLAUDE.md          ← this file
```

---

## Commands

```bash
# FastAPI backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
# Docs: http://localhost:8000/docs

# Streamlit dashboard
pip install -r frontend_py/requirements.txt
streamlit run frontend_py/app.py
# App: http://localhost:8501

# Next.js frontend
cd frontend && npm install && npm run dev
# App: http://localhost:3000

# Backend tests
pytest backend/tests/ -v

# Guardrail tests only
pytest backend/tests/ -v -m guardrail

# Databricks/PySpark tests
pytest databricks/tests/ -v -m databricks

# MCP server
pip install -r mcp_server/requirements.txt
mcp run mcp_server/server.py

# Databricks bundle deploy
databricks bundle deploy --target dev

# Terraform (AWS infra)
cd infra/aws && terraform init && terraform plan -var="env=dev"
```

---

## Key Design Decisions

### Compliance tags on DomainField
`DomainField` has `compliance_tags: list[str]` (e.g. `["GDPR", "CCPA"]`) and
`masking_strategy: str | None`. Known tags: GDPR, CCPA, PCI, HIPAA, SOC2.

### Job status sync (source field)
`GET /jobs/` returns `source: "live" | "stub"`. Streamlit shows a warning banner
when `source == "stub"` (Databricks credentials not configured).

### Medallion architecture
- Bronze = raw CSV/Parquet from S3, schema-on-read
- Silver = masked + transformed + `_tdm_*` lineage columns (pipeline_run_id, ingested_at, masking_applied)
- Gold = provision-ready curated outputs

### Masking
SHA-256 hash is deterministic — same input always produces same output, preserving
join stability across environments.

### Stub-first design
All API endpoints degrade gracefully to in-memory stubs when Databricks/AWS
credentials are absent — enabling full local development.

---

## Domains

| Domain | PII Fields | Compliance |
|---|---|---|
| customer | first_name, last_name, email, phone, ssn, address | GDPR, CCPA, HIPAA (ssn) |
| order | customer_id, billing_address, shipping_address | GDPR, CCPA |
| product | none | — |
| inventory | none | — |
| loyalty | customer_id, email | GDPR, CCPA |
| payment | customer_id, card_last4 | GDPR, CCPA, PCI |

---

## AWS Configuration

- Account: `910445327255`
- Region: `us-east-1`
- IAM role: `tdm-deckers-uc-access` (Databricks → S3 access)
- IAM user: `claude-adb-tdm-git` (CI/CD only)
- S3 bucket: `tdm-deckers-staged-dev`

## Databricks Configuration

- Workspace: `https://dbc-8402cc2e-6182.cloud.databricks.com`
- Catalog: `tdm_catalog`
- Dev schema: `tdm_dev`
- Staging schema: `tdm_staging`

---

## Non-functional Rules

- Never commit credentials — use `.env` (gitignored) and `~/.aws/credentials`
- Keep modules small and single-purpose
- All PII fields must have `compliance_tags` in `DomainField`
- Add `@pytest.mark.guardrail` to all PII/compliance tests
- Stub endpoints must always return `source: "stub"` in `JobRunList`
- GitHub remote: `https://github.com/pratikpdp99-lab/aws-adb-git.git`
