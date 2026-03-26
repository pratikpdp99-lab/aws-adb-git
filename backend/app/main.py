"""FastAPI entry point for the TDM platform backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import datasets, requests, health
from backend.app.routers import domains, masking, synthetic, jobs, lineage, recommendations, agents

app = FastAPI(
    title="TDM Deckers API",
    description="Test Data Management platform for retail — Databricks + AWS",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(datasets.router,  prefix="/datasets",  tags=["datasets"])
app.include_router(requests.router,  prefix="/requests",  tags=["requests"])
app.include_router(domains.router,   prefix="/domains",   tags=["domains"])
app.include_router(masking.router,   prefix="/masking",   tags=["masking"])
app.include_router(synthetic.router, prefix="/synthetic", tags=["synthetic"])
app.include_router(jobs.router,      prefix="/jobs",      tags=["jobs"])
app.include_router(lineage.router,         prefix="/lineage",      tags=["lineage"])
app.include_router(recommendations.router, prefix="/products",     tags=["recommendations"])
app.include_router(agents.router,         prefix="/agents",        tags=["agents"])
