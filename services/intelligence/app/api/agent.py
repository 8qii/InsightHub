from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.agents.core.models import AgentResult

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)

    model_config = {"str_strip_whitespace": True}


class AgentQueryResponse(BaseModel):
    answer: str
    sources: list[object]


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(payload: AgentQueryRequest, request: Request) -> AgentQueryResponse:
    agent = request.app.state.analyst_agent
    result: AgentResult = await agent.query(payload.question, request.state.request_id)
    return AgentQueryResponse(answer=result.answer, sources=result.sources)
