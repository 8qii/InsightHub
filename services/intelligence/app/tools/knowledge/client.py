from typing import Any
from urllib.parse import quote

import httpx

from app.tools.knowledge.exceptions import (
    KnowledgeAuthenticationError,
    KnowledgeInvalidResponse,
    KnowledgeProviderTimeout,
    KnowledgeProviderUnavailable,
    KnowledgeQueryFailed,
    KnowledgeWorkspaceNotFound,
)
from app.tools.knowledge.models import AnythingLLMChatResponse


class AnythingLLMClient:
    """HTTP adapter for the verified AnythingLLM Developer API contract."""

    def __init__(
        self,
        base_url: str | None,
        api_key: str | None,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        timeout = httpx.Timeout(timeout_seconds, connect=min(timeout_seconds, 5.0))
        self._client = httpx.AsyncClient(
            base_url=(base_url or "").rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=timeout,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def validate_credentials(self) -> bool:
        self._require_configuration()
        try:
            response = await self._client.get("/api/v1/auth")
        except httpx.TimeoutException as exc:
            raise KnowledgeProviderTimeout() from exc
        except httpx.RequestError as exc:
            raise KnowledgeProviderUnavailable() from exc

        if response.status_code in (401, 403):
            raise KnowledgeAuthenticationError()
        if response.status_code >= 500:
            raise KnowledgeProviderUnavailable()
        if response.status_code != 200:
            raise KnowledgeQueryFailed()

        body = self._parse_json(response)
        if not isinstance(body, dict) or body.get("authenticated") is not True:
            raise KnowledgeInvalidResponse()
        return True

    async def query(self, workspace_id: str, query: str) -> AnythingLLMChatResponse:
        self._require_configuration()
        try:
            response = await self._client.post(
                f"/api/v1/workspace/{quote(workspace_id, safe='')}/chat",
                json={"message": query, "mode": "query", "reset": False},
            )
        except httpx.TimeoutException as exc:
            raise KnowledgeProviderTimeout() from exc
        except httpx.RequestError as exc:
            raise KnowledgeProviderUnavailable() from exc

        if response.status_code in (401, 403):
            raise KnowledgeAuthenticationError()
        if response.status_code == 404 or (
            response.status_code == 400 and "workspace" in response.text.lower()
        ):
            raise KnowledgeWorkspaceNotFound()
        if response.status_code >= 500:
            raise KnowledgeProviderUnavailable()
        if response.status_code == 429:
            raise KnowledgeQueryFailed()
        if response.status_code >= 400:
            raise KnowledgeQueryFailed()

        try:
            body: Any = self._parse_json(response)
            return AnythingLLMChatResponse.model_validate(body)
        except (TypeError, ValueError) as exc:
            raise KnowledgeInvalidResponse() from exc

    @staticmethod
    def _parse_json(response: httpx.Response) -> Any:
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            raise KnowledgeInvalidResponse()
        try:
            return response.json()
        except ValueError as exc:
            raise KnowledgeInvalidResponse() from exc

    def _require_configuration(self) -> None:
        if not self._client.base_url or not self._api_key:
            raise KnowledgeProviderUnavailable()
