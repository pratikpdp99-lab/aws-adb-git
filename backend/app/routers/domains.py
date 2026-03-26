"""
Domain catalogue endpoints.
Returns metadata about each supported retail domain: fields, PII columns, row estimates.
"""

from fastapi import APIRouter, HTTPException
from backend.app.models import Domain, DomainField, DomainList

router = APIRouter()

# Domain registry — single source of truth for TDM domain metadata.
# In production this would be backed by Unity Catalog schema inspection.
_DOMAINS: dict[str, Domain] = {
    "customer": Domain(
        name="customer",
        description="Retail customer master data including PII contact fields.",
        fields=[
            DomainField(name="customer_id",   type="string",  pii=False, nullable=False),
            DomainField(name="first_name",     type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="last_name",      type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="email",          type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="phone",          type="string",  pii=True,  nullable=True,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="redact"),
            DomainField(name="ssn",            type="string",  pii=True,  nullable=True,
                        compliance_tags=["GDPR", "CCPA", "HIPAA"], masking_strategy="hash"),
            DomainField(name="address",        type="string",  pii=True,  nullable=True,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="redact"),
            DomainField(name="created_date",   type="date",    pii=False, nullable=True),
        ],
        pii_fields=["first_name", "last_name", "email", "phone", "ssn", "address"],
        supported_environments=["dev", "staging"],
        estimated_row_count=500_000,
    ),
    "order": Domain(
        name="order",
        description="Customer order transactions with fulfillment status.",
        fields=[
            DomainField(name="order_id",         type="string",  pii=False, nullable=False),
            DomainField(name="customer_id",       type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="order_date",        type="date",    pii=False, nullable=False),
            DomainField(name="total_amount",      type="double",  pii=False, nullable=False),
            DomainField(name="status",            type="string",  pii=False, nullable=False),
            DomainField(name="billing_address",   type="string",  pii=True,  nullable=True,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="redact"),
            DomainField(name="shipping_address",  type="string",  pii=True,  nullable=True,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="redact"),
        ],
        pii_fields=["customer_id", "billing_address", "shipping_address"],
        supported_environments=["dev", "staging"],
        estimated_row_count=2_000_000,
    ),
    "product": Domain(
        name="product",
        description="Product catalog — no PII, safe for all environments.",
        fields=[
            DomainField(name="product_id",  type="string",  pii=False, nullable=False),
            DomainField(name="name",        type="string",  pii=False, nullable=False),
            DomainField(name="category",    type="string",  pii=False, nullable=True),
            DomainField(name="price",       type="double",  pii=False, nullable=False),
            DomainField(name="in_stock",    type="boolean", pii=False, nullable=False),
        ],
        pii_fields=[],
        supported_environments=["dev", "staging", "prod"],
        estimated_row_count=50_000,
    ),
    "inventory": Domain(
        name="inventory",
        description="Store and warehouse inventory levels per product and location.",
        fields=[
            DomainField(name="inventory_id",  type="string",  pii=False, nullable=False),
            DomainField(name="product_id",    type="string",  pii=False, nullable=False),
            DomainField(name="location_id",   type="string",  pii=False, nullable=False),
            DomainField(name="quantity",      type="integer", pii=False, nullable=False),
            DomainField(name="updated_at",    type="timestamp",pii=False, nullable=True),
        ],
        pii_fields=[],
        supported_environments=["dev", "staging", "prod"],
        estimated_row_count=200_000,
    ),
    "loyalty": Domain(
        name="loyalty",
        description="Customer loyalty programme — points, tiers, redemptions.",
        fields=[
            DomainField(name="loyalty_id",    type="string",  pii=False, nullable=False,
                        compliance_tags=["CCPA"], masking_strategy="hash"),
            DomainField(name="customer_id",   type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="email",         type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="points",        type="integer", pii=False, nullable=False),
            DomainField(name="tier",          type="string",  pii=False, nullable=False),
            DomainField(name="enrolled_date", type="date",    pii=False, nullable=True),
        ],
        pii_fields=["customer_id", "email"],
        supported_environments=["dev", "staging"],
        estimated_row_count=300_000,
    ),
    "payment": Domain(
        name="payment",
        description="DTC payment transactions — PCI-scoped fields masked by default.",
        fields=[
            DomainField(name="payment_id",      type="string",  pii=False, nullable=False),
            DomainField(name="order_id",         type="string",  pii=False, nullable=False),
            DomainField(name="customer_id",      type="string",  pii=True,  nullable=False,
                        compliance_tags=["GDPR", "CCPA"], masking_strategy="hash"),
            DomainField(name="payment_method",   type="string",  pii=False, nullable=False),
            DomainField(name="card_last4",        type="string",  pii=True,  nullable=True,
                        compliance_tags=["PCI"], masking_strategy="hash"),
            DomainField(name="card_network",     type="string",  pii=False, nullable=True,
                        compliance_tags=["PCI"]),
            DomainField(name="amount",           type="double",  pii=False, nullable=False),
            DomainField(name="currency",         type="string",  pii=False, nullable=False),
            DomainField(name="status",           type="string",  pii=False, nullable=False),
            DomainField(name="gateway",          type="string",  pii=False, nullable=True),
            DomainField(name="created_at",       type="timestamp",pii=False, nullable=True),
        ],
        pii_fields=["customer_id", "card_last4"],
        supported_environments=["dev", "staging"],
        estimated_row_count=3_000_000,
    ),
}


@router.get("/", response_model=DomainList)
def list_domains(has_pii: bool = None):
    """List all supported data domains. Filter by has_pii=true|false."""
    results = list(_DOMAINS.values())
    if has_pii is not None:
        results = [d for d in results if bool(d.pii_fields) == has_pii]
    return DomainList(domains=results, total=len(results))


@router.get("/{domain_name}", response_model=Domain)
def get_domain(domain_name: str):
    """Get full metadata for a specific domain including all fields and PII tags."""
    domain = _DOMAINS.get(domain_name)
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' not found.")
    return domain
