from typing import Any

from pydantic import BaseModel, Field


class KnowledgeQueryRequest(BaseModel):
    workspace_id: str = Field(min_length=1, max_length=200)
    query: str = Field(min_length=1, max_length=10_000)

    model_config = {"str_strip_whitespace": True}


class KnowledgeSource(BaseModel):
    source_id: str
    title: str
    uri: str | None = None
    excerpt: str | None = None
    score: float | None = None
    page: int | None = None


class KnowledgeQueryResult(BaseModel):
    answer: str
    sources: list[KnowledgeSource]
    latency_ms: int
    request_id: str


class AnythingLLMChatResponse(BaseModel):
    """The small upstream response subset used by the adapter."""

    text_response: str = Field(alias="textResponse")
    sources: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"extra": "ignore", "populate_by_name": True}
