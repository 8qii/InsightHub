import logging
import time
from typing import Any

from app.tools.knowledge.client import AnythingLLMClient
from app.tools.knowledge.exceptions import KnowledgeInvalidResponse
from app.tools.knowledge.models import KnowledgeQueryResult, KnowledgeSource

logger = logging.getLogger("insighthub.knowledge")


class KnowledgeService:
    def __init__(self, client: AnythingLLMClient) -> None:
        self._client = client

    async def query(self, workspace_id: str, query: str, request_id: str) -> KnowledgeQueryResult:
        started_at = time.perf_counter()
        result = await self._client.query(workspace_id, query)
        if not result.text_response.strip():
            raise KnowledgeInvalidResponse()
        sources = self._normalize_sources(result.sources)
        latency_ms = round((time.perf_counter() - started_at) * 1000)
        logger.info(
            "Knowledge query completed",
            extra={
                "request_id": request_id,
                "workspace_id": workspace_id,
                "query_length": len(query),
                "upstream_duration_ms": latency_ms,
                "source_count": len(sources),
                "result_status": "success",
            },
        )
        return KnowledgeQueryResult(
            answer=result.text_response,
            sources=sources,
            latency_ms=latency_ms,
            request_id=request_id,
        )

    @staticmethod
    def _normalize_sources(raw_sources: list[dict[str, Any]]) -> list[KnowledgeSource]:
        normalized: list[KnowledgeSource] = []
        seen: set[str] = set()
        for raw_source in raw_sources:
            title = _as_string(raw_source.get("title"))
            uri = _as_string(raw_source.get("url") or raw_source.get("uri"))
            source_id = _as_string(raw_source.get("id")) or uri or title
            if not source_id or not title or source_id in seen:
                continue
            seen.add(source_id)
            score = raw_source.get("score")
            page = raw_source.get("page")
            normalized.append(
                KnowledgeSource(
                    source_id=source_id,
                    title=title,
                    uri=uri,
                    excerpt=_as_string(raw_source.get("chunk") or raw_source.get("text")),
                    score=score if isinstance(score, int | float) else None,
                    page=page if isinstance(page, int) else None,
                )
            )
        return normalized


def _as_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
