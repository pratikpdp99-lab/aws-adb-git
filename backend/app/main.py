"""FastAPI entry point for the TDM platform backend."""

from fastapi import FastAPI
from backend.app.routers import datasets, requests, health

app = FastAPI(
    title="TDM Deckers API",
    description="Test Data Management platform for retail — Databricks + AWS",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
app.include_router(requests.router, prefix="/requests", tags=["requests"])
