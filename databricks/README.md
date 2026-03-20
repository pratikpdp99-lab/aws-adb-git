# databricks/

PySpark pipeline modules and Databricks Asset Bundle (DAB) configuration for tdm-deckers.

## Structure

```
bundles/
  databricks.yml     DAB config — jobs, clusters, targets (dev/staging/prod)
notebooks/
  explore_source.py  Exploratory notebook for inspecting bronze/silver tables
src/
  ingest.py          Read from S3 → write to Bronze Delta tables
  mask.py            PII masking and SHA-256 tokenization
  synthetic.py       Fake data generation per domain
  subset.py          Referentially consistent subsetting anchored on customer IDs
tests/
  test_mask.py
  test_synthetic.py
```

## Pipeline flow

```
S3 (raw) → ingest → Bronze (Delta) → mask → Silver (Delta) → subset/synthetic → lower env
```

## Local run

```bash
pip install pyspark pytest
pytest databricks/tests/
```

## Deploy with DAB

```bash
pip install databricks-cli
databricks bundle validate --target dev
databricks bundle deploy --target dev
databricks bundle run tdm_ingest_job --target dev
```

## Environment variables (set in .env or DAB target)

| Variable           | Description                        |
|--------------------|------------------------------------|
| `DATABRICKS_HOST`  | Workspace URL                      |
| `DATABRICKS_TOKEN` | Personal access token              |
| `AWS_REGION`       | AWS region for S3 access           |
