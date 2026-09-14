from typing import cast

from fastapi import APIRouter, Depends, Request

from app.tools.knowledge.models import KnowledgeQueryRequest, KnowledgeQueryResult
from app.tools.knowledge.service import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


def get_knowledge_service(request: Request) -> KnowledgeService:
    return cast(KnowledgeService, request.app.state.knowledge_service)


@router.post("/query", response_model=KnowledgeQueryResult)
async def query_knowledge(
    payload: KnowledgeQueryRequest,
    request: Request,
    service: KnowledgeService = Depends(get_knowledge_service),  # noqa: B008
) -> KnowledgeQueryResult:
    return await service.query(
        workspace_id=payload.workspace_id,
        query=payload.query,
        request_id=request.state.request_id,
    )
