import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.knowledge import get_knowledge_service
from app.main import app
from app.tools.knowledge.client import AnythingLLMClient
from app.tools.knowledge.exceptions import (
    KnowledgeAuthenticationError,
    KnowledgeInvalidResponse,
    KnowledgeProviderTimeout,
    KnowledgeProviderUnavailable,
    KnowledgeQueryFailed,
    KnowledgeWorkspaceNotFound,
)
from app.tools.knowledge.service import KnowledgeService

TransportHandler = Callable[[httpx.Request], Awaitable[httpx.Response]]


def make_client(handler: TransportHandler) -> AnythingLLMClient:
    return AnythingLLMClient(
        base_url="http://anythingllm.test",
        api_key="test-api-key",
        timeout_seconds=1,
        transport=httpx.MockTransport(handler),
    )


def json_response(status_code: int, body: Any) -> httpx.Response:
    return httpx.Response(status_code, json=body)


def test_successful_query_normalizes_and_deduplicates_sources() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/workspace/nova-retail/chat"
        assert request.headers["Authorization"] == "Bearer test-api-key"
        assert request.read() == (
            b'{"message":"What is the VIP discount?","mode":"query","reset":false}'
        )
        return json_response(
            200,
            {
                "textResponse": "VIP customers may receive up to 12%.",
                "sources": [
                    {
                        "id": "policy-1",
                        "title": "sales-policy.pdf",
                        "chunk": "Up to 12%.",
                        "score": 0.9,
                        "page": 2,
                    },
                    {"id": "policy-1", "title": "sales-policy.pdf", "chunk": "duplicate"},
                    {"title": "terms.docx", "chunk": "Terms"},
                    {"title": "ignored-extra", "unknown": True},
                ],
                "unknownField": "ignored",
            },
        )

    client = make_client(handler)
    try:
        result = asyncio.run(
            KnowledgeService(client).query(
                "nova-retail", "What is the VIP discount?", "request-1"
            )
        )
    finally:
        asyncio.run(client.close())

    assert result.answer == "VIP customers may receive up to 12%."
    assert result.request_id == "request-1"
    assert len(result.sources) == 3
    assert result.sources[0].page == 2
    assert result.sources[0].score == 0.9


def test_successful_query_allows_no_citations() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return json_response(200, {"textResponse": "No source was needed.", "sources": []})

    client = make_client(handler)
    try:
        result = asyncio.run(
            KnowledgeService(client).query("nova-retail", "Question", "request-2")
        )
    finally:
        asyncio.run(client.close())

    assert result.sources == []


def test_empty_answer_is_invalid() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return json_response(200, {"textResponse": "   ", "sources": []})

    client = make_client(handler)
    try:
        with pytest.raises(KnowledgeInvalidResponse):
            asyncio.run(KnowledgeService(client).query("nova-retail", "Question", "request-3"))
    finally:
        asyncio.run(client.close())


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (401, KnowledgeAuthenticationError),
        (403, KnowledgeAuthenticationError),
        (404, KnowledgeWorkspaceNotFound),
        (429, KnowledgeQueryFailed),
        (500, KnowledgeProviderUnavailable),
        (503, KnowledgeProviderUnavailable),
    ],
)
def test_upstream_statuses_map_to_stable_exceptions(
    status_code: int, expected: type[Exception]
) -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        body = {"error": "Workspace not found"} if status_code == 404 else {"error": "failure"}
        return json_response(status_code, body)

    client = make_client(handler)
    try:
        with pytest.raises(expected):
            asyncio.run(client.query("nova-retail", "Question"))
    finally:
        asyncio.run(client.close())


def test_timeout_and_connection_errors_are_mapped() -> None:
    async def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    async def connection_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    timeout_client = make_client(timeout_handler)
    connection_client = make_client(connection_handler)
    try:
        with pytest.raises(KnowledgeProviderTimeout):
            asyncio.run(timeout_client.query("nova-retail", "Question"))
        with pytest.raises(KnowledgeProviderUnavailable):
            asyncio.run(connection_client.query("nova-retail", "Question"))
    finally:
        asyncio.run(timeout_client.close())
        asyncio.run(connection_client.close())


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b"not-json", headers={"content-type": "text/html"}),
        httpx.Response(200, content=b"{}", headers={"content-type": "application/json"}),
        httpx.Response(200, json={"textResponse": "answer", "sources": "invalid"}),
    ],
)
def test_malformed_success_responses_are_rejected(response: httpx.Response) -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return response

    client = make_client(handler)
    try:
        with pytest.raises(KnowledgeInvalidResponse):
            asyncio.run(client.query("nova-retail", "Question"))
    finally:
        asyncio.run(client.close())


def test_validate_credentials_uses_auth_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/auth"
        return json_response(200, {"authenticated": True})

    client = make_client(handler)
    try:
        assert asyncio.run(client.validate_credentials()) is True
    finally:
        asyncio.run(client.close())


def test_api_success_and_request_id_propagation() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return json_response(
            200,
            {
                "textResponse": "The answer",
                "sources": [{"title": "policy.pdf", "chunk": "Evidence"}],
            },
        )

    client = make_client(handler)
    service = KnowledgeService(client)
    app.dependency_overrides[get_knowledge_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/v1/knowledge/query",
            headers={"X-Request-ID": "api-request-1"},
            json={"workspace_id": "nova-retail", "query": "Question"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "api-request-1"
    assert response.json()["answer"] == "The answer"
    assert response.json()["sources"][0]["title"] == "policy.pdf"


def test_api_rejects_empty_and_oversized_queries() -> None:
    app.dependency_overrides[get_knowledge_service] = lambda: KnowledgeService(
        make_client(lambda _: json_response(500, {}))
    )
    try:
        client = TestClient(app)
        empty_response = client.post(
            "/api/v1/knowledge/query",
            json={"workspace_id": "nova-retail", "query": "   "},
        )
        oversized_response = client.post(
            "/api/v1/knowledge/query",
            json={"workspace_id": "nova-retail", "query": "x" * 10_001},
        )
    finally:
        app.dependency_overrides.clear()

    assert empty_response.status_code == 422
    assert oversized_response.status_code == 422


def test_api_maps_provider_failures_without_leaking_secrets() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return json_response(503, {"error": "internal provider details"})

    app.dependency_overrides[get_knowledge_service] = lambda: KnowledgeService(make_client(handler))
    try:
        response = TestClient(app).post(
            "/api/v1/knowledge/query",
            json={"workspace_id": "nova-retail", "query": "Question"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "test-api-key" not in response.text
    assert "internal provider details" not in response.text
