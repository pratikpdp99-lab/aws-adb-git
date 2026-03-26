"""
Catalog agent — answers questions about TDM data domains using Claude.
Fetches live domain metadata from the API and uses it as context.
"""

import os
import httpx

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

_API_BASE  = os.getenv("TDM_API_URL", "http://localhost:8000")
_MODEL     = "claude-sonnet-4-6"
_MAX_TOKENS = 1024

_SYSTEM = (
    "You are a TDM data catalog assistant for Deckers Brands. "
    "Answer questions about data domains, PII fields, compliance tags, lineage, "
    "and masking policies using the provided context. "
    "Be concise and reference specific field names and compliance tags where relevant. "
    "If information is not in the context, say so rather than guessing."
)


def _fetch_context() -> dict:
    """Fetch domain, masking policy, and lineage context from the API."""
    ctx: dict = {}
    try:
        with httpx.Client(base_url=_API_BASE, timeout=10) as client:
            ctx["domains"] = client.get("/domains/").json()
            ctx["masking_policies"] = client.get("/masking/policies").json()
    except Exception as e:
        ctx["error"] = str(e)
    return ctx


def answer(question: str) -> str:
    """Answer a catalog question using live API context + Claude."""
    if not _ANTHROPIC_AVAILABLE:
        return "anthropic package not installed. Run: pip install anthropic"

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        return (
            "ANTHROPIC_API_KEY is not set. "
            "Set it in your .env file to enable the catalog agent."
        )

    ctx = _fetch_context()
    context_str = (
        f"## TDM Catalog Context\n\n"
        f"### Domains\n{ctx.get('domains', 'Not available')}\n\n"
        f"### Masking Policies\n{ctx.get('masking_policies', 'None defined')}\n"
    )
    if "error" in ctx:
        context_str += f"\n### Fetch Error\n{ctx['error']}"

    client = anthropic.Anthropic(api_key=anthropic_key)
    message = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"{context_str}\n\n## Question\n{question}",
            }
        ],
    )
    return message.content[0].text
