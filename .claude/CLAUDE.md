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

# Project: tdm-deckers

## Purpose
Build an enterprise-grade Test Data Management (TDM) platform for retail using Databricks, AWS, GitHub, and a modern frontend.

The platform should support masked data provisioning, synthetic data generation, subsetting, referential integrity, test data request workflows, auditability, lineage, and data cataloging.

## Business Context
This project is for a retail-oriented TDM platform. Typical business domains include:
- customer
- order
- product
- inventory
- store
- loyalty
- pricing
- promotion
- shipment
- payment

The platform should support lower environments such as:
- dev
- qa
- uat
- perf

## Core Capabilities
1. Ingest source retail data from AWS S3 and other sources
2. Profile and classify sensitive fields
3. Apply masking and tokenization rules
4. Generate synthetic test data for selected domains
5. Create subset datasets while preserving referential integrity
6. Provision approved datasets to target environments
7. Track lineage and metadata using Databricks Unity Catalog
8. Expose APIs for data request and provisioning workflow
9. Provide a frontend for request, approval, job tracking, and dataset browsing
10. Maintain audit logs and role-aware access

## Preferred Technology Stack
### Data Platform
- Databricks
- PySpark
- Delta Lake
- Unity Catalog
- Databricks SQL
- Databricks Jobs or Databricks Asset Bundles

### Cloud
- AWS
- S3
- IAM
- Secrets Manager if needed

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy only if truly needed
- boto3
- databricks SDK or connector where appropriate

### Frontend
- React
- Next.js preferred
- TypeScript
- Tailwind CSS
- clean enterprise UX

### DevOps
- GitHub
- GitHub Actions
- environment-driven configuration
- no hardcoded secrets

## Authentication and Environment Rules
- Never hardcode credentials, tokens, URLs, or secrets
- Use environment variables, AWS named profiles, and Databricks profiles
- Assume AWS profile name is `deckers-dev` unless changed in config
- Use config files and `.env.example`, never commit live secrets
- Keep `.gitignore` updated for secret-bearing files

## Databricks Design Expectations
- Use medallion-like layering where useful:
  - bronze = raw or landed
  - silver = standardized and masked
  - gold = provision-ready curated TDM outputs
- Register important datasets in Unity Catalog
- Favor transformations that preserve lineage visibility in Databricks
- Organize jobs, notebooks, and code in a deployable project layout
- Prefer modular Python packages over large notebooks when possible

## TDM Design Principles
- Preserve referential integrity across related datasets
- Support both masked production-like data and fully synthetic data
- Make masking deterministic where business use requires stable joins
- Support domain-based extraction and subset filtering
- Make provisioning reproducible and auditable
- Allow policy-driven field handling:
  - mask
  - tokenize
  - null out
  - synthesize
  - retain if non-sensitive and approved

## API Design Expectations
The backend should eventually support endpoints for:
- health
- list domains
- profile dataset
- classify columns
- submit masking policy
- request subset dataset
- request synthetic dataset
- start provisioning job
- list job status
- list available datasets
- fetch lineage summary
- fetch audit events

Use clean request and response models.
Keep API contracts consistent and typed.

## Frontend Expectations
The frontend should eventually include:
- landing/dashboard page
- dataset catalog page
- request test data form
- masking policy review page
- job status page
- lineage and catalog page
- admin/settings page

Design should feel like an enterprise internal platform:
- clear navigation
- low clutter
- status visibility
- auditability
- searchable lists and tables

## Code Quality Rules
- Keep modules small and focused
- Add docstrings for non-trivial logic
- Add type hints
- Add tests for backend services and important transformation logic
- Prefer readable code over overly clever abstractions
- Do not create large monolithic files
- Update README files when creating new modules

## Testing Expectations
Add tests for:
- masking logic
- synthetic data generation rules
- referential integrity checks
- API request validation
- service-layer behavior
- config parsing

## Deliverable Style
When asked to generate code:
- first inspect existing project structure
- follow the repository conventions already present
- create minimal but working code
- add TODO comments only where external setup is required
- provide local run instructions in README
- do not invent fake secrets or fake production values

## Initial Build Roadmap
Phase 1:
- scaffold repository
- create configuration model
- add backend skeleton
- add frontend skeleton
- add Databricks module skeleton
- add sample retail domain metadata

Phase 2:
- build masking engine
- build synthetic data generator
- build subset engine
- build S3 integration
- build Databricks ingestion and Delta write flows

Phase 3:
- build request workflow APIs
- build frontend pages
- connect frontend to backend
- add job tracking and audit model

Phase 4:
- add Unity Catalog integration, lineage views, and deployment workflows

## Important Constraints
- Do not delete user-authored files unless explicitly asked
- Do not refactor the whole project unless requested
- Do not expose secrets in logs or sample code
- Do not assume production access
- Use mock or sample data where real data is unavailable

## Preferred Working Pattern
When implementing a major feature:
1. inspect repository structure
2. propose touched files
3. implement code
4. add tests
5. update README or usage instructions

## Primary Goal
Help build a practical, extensible, enterprise TDM platform that can be demoed, evolved, and deployed incrementally.
