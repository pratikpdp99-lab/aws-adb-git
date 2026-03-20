# backend/

FastAPI backend for the TDM Deckers platform.

## Structure

```
app/
  main.py            FastAPI app — mounts all routers
  models.py          Pydantic models (Dataset, DataRequest, enums)
  connection.py      AWS + Databricks client factory
  routers/
    health.py        GET /health
    datasets.py      GET /datasets, GET /datasets/{id}
    requests.py      POST/GET/PATCH /requests
tests/
  test_datasets.py
  test_requests.py
requirements.txt
```

## Local run

```bash
pip install -r backend/requirements.txt
cp .env.example .env

# Start API server
uvicorn backend.app.main:app --reload --port 8000
```

API docs auto-generated at: http://localhost:8000/docs

## Run tests

```bash
pytest backend/tests/ -v
```

## Endpoints

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | /health                     | Health check                 |
| GET    | /datasets/                  | List datasets (filter by domain/env) |
| GET    | /datasets/{id}              | Get dataset by ID            |
| POST   | /requests/                  | Submit a data request        |
| GET    | /requests/                  | List requests (filter by status) |
| GET    | /requests/{id}              | Get request by ID            |
| PATCH  | /requests/{id}/approve      | Approve a request            |

## Environment variables

| Variable           | Description                    |
|--------------------|--------------------------------|
| `DATABRICKS_HOST`  | Workspace URL                  |
| `DATABRICKS_TOKEN` | Personal access token          |
| `AWS_REGION`       | AWS region (default us-east-1) |
