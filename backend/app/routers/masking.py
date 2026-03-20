"""
Masking policy endpoints.
Allows teams to define and manage per-domain field masking rules.
Policies are applied by the Databricks pipeline during Silver layer transforms.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from backend.app.models import MaskingPolicy, MaskingPolicyCreate, SUPPORTED_DOMAINS
from backend.app.config import Settings, get_settings

router = APIRouter()

# In-memory store — replace with a persistent DB or Delta table in production
_POLICIES: dict[str, MaskingPolicy] = {}
_counter = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/policies", response_model=MaskingPolicy, status_code=201)
def submit_masking_policy(
    body: MaskingPolicyCreate,
    settings: Settings = Depends(get_settings),
):
    """Submit or replace a masking policy for a domain.
    If a policy already exists for the domain, its version is incremented.
    """
    global _counter
    if body.domain not in SUPPORTED_DOMAINS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported domain '{body.domain}'. Must be one of {SUPPORTED_DOMAINS}.",
        )

    existing = _POLICIES.get(body.domain)
    version  = (existing.version + 1) if existing else 1

    policy = MaskingPolicy(
        id=f"POL-{_counter:04d}",
        domain=body.domain,
        rules=body.rules,
        created_by=body.created_by,
        version=version,
        created_at=_now(),
    )
    _POLICIES[body.domain] = policy
    _counter += 1
    return policy


@router.get("/policies", response_model=list[MaskingPolicy])
def list_masking_policies():
    """List all active masking policies (one per domain)."""
    return list(_POLICIES.values())


@router.get("/policies/{domain}", response_model=MaskingPolicy)
def get_masking_policy(domain: str):
    """Get the active masking policy for a domain."""
    policy = _POLICIES.get(domain)
    if not policy:
        raise HTTPException(
            status_code=404,
            detail=f"No masking policy found for domain '{domain}'.",
        )
    return policy


@router.put("/policies/{domain}", response_model=MaskingPolicy)
def update_masking_policy(domain: str, body: MaskingPolicyCreate):
    """Update an existing masking policy. Increments version."""
    existing = _POLICIES.get(domain)
    if not existing:
        raise HTTPException(status_code=404, detail=f"No policy for domain '{domain}'. Use POST to create.")
    if body.domain != domain:
        raise HTTPException(status_code=422, detail="Domain in body must match path parameter.")

    updated = MaskingPolicy(
        id=existing.id,
        domain=domain,
        rules=body.rules,
        created_by=body.created_by,
        version=existing.version + 1,
        created_at=_now(),
    )
    _POLICIES[domain] = updated
    return updated


@router.delete("/policies/{domain}", status_code=204)
def delete_masking_policy(domain: str):
    """Remove the masking policy for a domain."""
    if domain not in _POLICIES:
        raise HTTPException(status_code=404, detail=f"No policy for domain '{domain}'.")
    del _POLICIES[domain]
