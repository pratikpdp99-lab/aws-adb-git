"""
Dataset endpoints — browse and retrieve available TDM datasets.
"""

from fastapi import APIRouter, HTTPException
from backend.app.models import Dataset, DatasetList

router = APIRouter()

# Stub in-memory store — replace with Unity Catalog / DB query
_DATASETS: dict[str, Dataset] = {
    "ds-001": Dataset(
        id="ds-001",
        name="Customer Gold - Masked",
        domain="customer",
        environment="dev",
        row_count=10000,
        masking_applied=True,
    ),
    "ds-002": Dataset(
        id="ds-002",
        name="Order Subset Q1 2024",
        domain="order",
        environment="staging",
        row_count=5000,
        masking_applied=True,
    ),
}


@router.get("/", response_model=DatasetList)
def list_datasets(domain: str = None, environment: str = None):
    """List all available datasets, optionally filtered by domain or environment."""
    results = list(_DATASETS.values())
    if domain:
        results = [d for d in results if d.domain == domain]
    if environment:
        results = [d for d in results if d.environment == environment]
    return DatasetList(datasets=results, total=len(results))


@router.get("/{dataset_id}", response_model=Dataset)
def get_dataset(dataset_id: str):
    """Get details for a specific dataset."""
    dataset = _DATASETS.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")
    return dataset
