# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project: tdm-deckers

## Goal
Build an enterprise TDM platform for retail on Databricks + AWS.

## Core capabilities
- Source onboarding for retail domains: customer, order, product, inventory, loyalty
- Sensitive data masking/tokenization
- Synthetic data generation for lower environments
- Data subsetting with referential integrity
- Test data request APIs
- Auditability and role-based access
- Data cataloging and lineage using Unity Catalog
- Frontend for request, approval, dataset browsing, and environment release status

## Preferred stack
- Python, PySpark, Databricks SQL
- Databricks Asset Bundles (declarative automation)
- FastAPI backend
- React/Next.js frontend
- AWS S3 for staged data
- Terraform only if needed

## Repository Structure

```
backend/
  app/
    main.py          FastAPI entry point — mounts all routers
    models.py        Pydantic models (Dataset, DataRequest, enums)
    connection.py    AWS + Databricks client factory
    routers/
      health.py      GET /health
      datasets.py    GET /datasets, GET /datasets/{id}
      requests.py    POST/GET/PATCH /requests
  tests/
  requirements.txt   fastapi, uvicorn, pydantic, databricks-sdk, boto3, pytest

databricks/
  bundles/
    databricks.yml   DAB config — jobs, clusters, dev/staging/prod targets
  notebooks/
    explore_source.py  Exploration notebook for bronze/silver tables
  src/
    ingest.py        S3 → Bronze Delta (per domain)
    mask.py          SHA-256 tokenization + redaction of PII fields
    synthetic.py     Fake record generation per domain
    subset.py        Referentially consistent subsetting anchored on customer IDs
  tests/
    test_mask.py
    test_synthetic.py

frontend/
  src/
    pages/
      index.tsx      Dataset browser
      requests.tsx   Test data request form
    components/
      DatasetCard.tsx
  .env.local.example
  package.json       Next.js 14 + TypeScript

infra/
  aws/
    main.tf          AWS provider config
    s3.tf            Staged data S3 bucket (versioned + encrypted)
    iam.tf           IAM policy for Databricks → S3 access
  databricks/
    workspace.tf     Databricks provider + Unity Catalog stubs

docs/
```

## Development Setup

```bash
# Backend
pip install -r backend/requirements.txt
cp .env.example .env          # fill in DATABRICKS_HOST and DATABRICKS_TOKEN
aws configure                 # set AWS credentials (stored in ~/.aws/credentials)

# Frontend
cd frontend && npm install
```

## Commands

```bash
# Verify AWS + Databricks connections
python backend/app/connection.py

# Run FastAPI server
uvicorn backend.app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs

# Run backend tests
pytest backend/tests/ -v

# Run Databricks pipeline tests (requires pyspark)
pytest databricks/tests/ -v

# Run frontend dev server
cd frontend && npm install && npm run dev
# App: http://localhost:3000

# Deploy Databricks Asset Bundle
databricks bundle deploy --target dev

# Terraform (AWS infra)
cd infra/aws && terraform init && terraform plan -var="env=dev"
```

## Connections (`backend/app/connection.py`)

Single entry point for all platform clients:

```python
from backend.app.connection import get_databricks_client, get_aws_session, get_s3_client

w   = get_databricks_client()   # Databricks WorkspaceClient
s3  = get_s3_client()           # boto3 S3 client
ses = get_aws_session()         # boto3 Session (for any AWS service)
```

### Databricks
Credentials from `.env`:
- `DATABRICKS_HOST` — workspace URL (`https://dbc-8402cc2e-6182.cloud.databricks.com`)
- `DATABRICKS_TOKEN` — personal access token

### AWS
Credentials from `~/.aws/credentials` (IAM user: `claude-adb-tdm-git`, Account: `910445327255`):
- Default region: `us-east-1` (override via `AWS_REGION` in `.env`)

## Non-functional rules
- Always use env vars or profiles for credentials — never commit secrets
- Keep modules small and single-purpose
- Add tests for transformation and API code
- Update README when new modules are added

## Development Context
- **Remote**: `https://github.com/pratikpdp99-lab/aws-adb-git.git`
- **Primary branch**: `main`
