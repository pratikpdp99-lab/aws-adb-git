"""
Agent endpoints — exposes Catalog and DQ Monitor agents as REST endpoints.
POST /agents/catalog  — catalog Q&A via Claude
POST /agents/dq       — DQ monitoring Q&A via Claude
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.agents.catalog_agent import answer as catalog_answer
from backend.app.agents.dq_agent import summarize as dq_summarize

router = APIRouter()


class AgentRequest(BaseModel):
    question: str


class AgentResponse(BaseModel):
    answer: str


@router.post("/catalog", response_model=AgentResponse)
def catalog_agent(body: AgentRequest) -> AgentResponse:
    """Ask the catalog agent a question about domains, PII, compliance, or lineage."""
    return AgentResponse(answer=catalog_answer(body.question))


@router.post("/dq", response_model=AgentResponse)
def dq_agent(body: AgentRequest) -> AgentResponse:
    """Ask the DQ monitor agent about recent job run quality results."""
    return AgentResponse(answer=dq_summarize(body.question))
