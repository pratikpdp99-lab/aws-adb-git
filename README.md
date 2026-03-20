# tdm-deckers

Enterprise Test Data Management (TDM) platform for retail, built on Databricks and AWS.

## Capabilities
- Source onboarding: customer, order, product, inventory, loyalty domains
- Sensitive data masking and tokenization
- Synthetic data generation for lower environments
- Data subsetting with referential integrity
- Test data request APIs with approval workflows
- Unity Catalog integration for lineage and governance

## Stack
- **Backend**: Python, FastAPI
- **Data platform**: Databricks (PySpark, SQL, Asset Bundles)
- **Storage**: AWS S3
- **Frontend**: Next.js / React
- **Infra**: Databricks Asset Bundles, Terraform (if needed)

## Structure
```
backend/       FastAPI app and connection utilities
databricks/    PySpark jobs, notebooks, DAB configs
frontend/      Next.js UI
infra/         AWS and Databricks infrastructure configs
docs/          Architecture and design docs
```

## Setup
```bash
# Backend
pip install -r backend/requirements.txt
cp .env.example .env
aws configure   # set AWS credentials

# Frontend
cd frontend && npm install
```

## Verify connections
```bash
python backend/app/connection.py
```
