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
  app/           FastAPI application code; connection.py is the entry point for all AWS/Databricks clients
  tests/         pytest tests for API and transformation logic
  requirements.txt
databricks/
  bundles/       Databricks Asset Bundle (DAB) YAML configs
  notebooks/     Exploratory and pipeline notebooks
  src/           PySpark transformation modules
  tests/         PySpark unit tests
frontend/
  src/           Next.js pages and components
  public/        Static assets
  package.json
infra/
  aws/           AWS infrastructure (S3 buckets, IAM, etc.)
  databricks/    Databricks workspace config
docs/            Architecture and design docs
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
# Verify both connections
python backend/app/connection.py

# Run backend tests
pytest backend/tests/

# Run frontend dev server
cd frontend && npm run dev

# Run frontend build
cd frontend && npm run build
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
