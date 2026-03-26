"""
DQ Monitor agent — summarises data quality results from recent job runs.
Fetches job list from the API and uses Claude to explain pass/fail state.
"""

import os
import httpx

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

_API_BASE   = os.getenv("TDM_API_URL", "http://localhost:8000")
_MODEL      = "claude-sonnet-4-6"
_MAX_TOKENS = 1024

_SYSTEM = (
    "You are a data quality monitoring assistant for the TDM platform at Deckers Brands. "
    "Answer questions about recent pipeline job runs, DQ check results, and failures. "
    "Be concise and specific. When jobs have failed, explain what likely went wrong "
    "based on the available context."
)


def _fetch_jobs(limit: int = 10) -> list:
    try:
        with httpx.Client(base_url=_API_BASE, timeout=10) as client:
            data = client.get(f"/jobs/?limit={limit}").json()
            return data.get("runs", [])
    except Exception:
        return []


def summarize(question: str) -> str:
    """Answer a DQ monitoring question using recent job data + Claude."""
    if not _ANTHROPIC_AVAILABLE:
        return "anthropic package not installed. Run: pip install anthropic"

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        return (
            "ANTHROPIC_API_KEY is not set. "
            "Set it in your .env file to enable the DQ monitor agent."
        )

    runs = _fetch_jobs()
    if not runs:
        jobs_ctx = "No recent job runs available."
    else:
        lines = []
        for r in runs[:10]:
            err = f" | error: {r['error_message']}" if r.get("error_message") else ""
            lines.append(
                f"- run_id={r['run_id']} job={r['job_name']} "
                f"status={r['status']} start={r.get('start_time', '?')}{err}"
            )
        jobs_ctx = "\n".join(lines)

    context_str = f"## Recent TDM Job Runs\n\n{jobs_ctx}"

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
