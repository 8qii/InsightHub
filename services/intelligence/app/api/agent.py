import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from app.agents.core.models import AgentResult
from app.observability.runs import RunStore, default_run_store

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)

    model_config = {"str_strip_whitespace": True}


class AgentQueryResponse(BaseModel):
    answer: str
    sources: list[object]


def _run_store(request: Request) -> RunStore:
    return getattr(request.app.state, "run_store", default_run_store)


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(payload: AgentQueryRequest, request: Request) -> AgentQueryResponse:
    agent = request.app.state.analyst_agent
    result: AgentResult = await agent.query(payload.question, request.state.request_id)
    _run_store(request).record(result)
    return AgentQueryResponse(answer=result.answer, sources=result.sources)


@router.get("/runs/{run_id}")
async def get_agent_run(run_id: str, request: Request) -> dict[str, object]:
    run = _run_store(request).get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run was not found.")
    return run.as_dict()


@router.post("/query/stream")
async def stream_agent_query(payload: AgentQueryRequest, request: Request) -> StreamingResponse:
    agent = request.app.state.analyst_agent

    async def events() -> AsyncIterator[str]:
        try:
            result: AgentResult = await agent.query(payload.question, request.state.request_id)
            _run_store(request).record(result)
            yield _sse("run", {"run_id": result.run_id, "status": "completed"})
            for chunk in _answer_chunks(result.answer):
                yield _sse("token", {"text": chunk})
                await asyncio.sleep(0)
            yield _sse("done", {"run_id": result.run_id, "sources": result.sources})
        except Exception as exc:
            yield _sse("error", {"message": _safe_stream_error(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _answer_chunks(answer: str, chunk_size: int = 48) -> list[str]:
    chunks: list[str] = []
    current = ""
    for word in answer.split(" "):
        candidate = f"{current} {word}" if current else word
        if current and len(candidate) > chunk_size:
            chunks.append(current)
            current = word
        else:
            current = candidate
    if current:
        chunks.append(current)
    return [f"{chunk} " for chunk in chunks[:-1]] + chunks[-1:] if chunks else []


def _safe_stream_error(error: Exception) -> str:
    if isinstance(error, HTTPException):
        return str(error.detail)
    return "The analyst could not complete this request."
