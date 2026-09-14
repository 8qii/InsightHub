from typing import Any

import httpx

from app.agents.core.models import LLMResponse, LLMToolCall
from app.errors import AppError


class OpenAICompatibleClient:
    """Small chat-completions client for OpenAI-compatible hosted models."""

    def __init__(
        self,
        base_url: str | None,
        api_key: str | None,
        model: str | None,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = (base_url or "").rstrip("/")
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=httpx.Timeout(timeout_seconds, connect=min(timeout_seconds, 5.0)),
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        if not self._base_url or not self._api_key or not self._model:
            raise AppError(503, "llm_not_configured", "The language model is not configured.")

        try:
            response = await self._client.post(
                "/chat/completions",
                json={
                    "model": self._model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
        except httpx.TimeoutException as exc:
            raise AppError(504, "llm_timeout", "The language model timed out.") from exc
        except httpx.RequestError as exc:
            raise AppError(503, "llm_unavailable", "The language model is unavailable.") from exc

        if response.status_code >= 500:
            raise AppError(503, "llm_unavailable", "The language model is unavailable.")
        if response.status_code >= 400:
            raise AppError(502, "llm_request_failed", "The language model rejected the request.")

        try:
            body = response.json()
            message = body["choices"][0]["message"]
            raw_tool_calls = message.get("tool_calls") or []
            tool_calls = [
                LLMToolCall(
                    call_id=call.get("id", ""),
                    name=call["function"]["name"],
                    arguments=call["function"].get("arguments", "{}"),
                )
                for call in raw_tool_calls
            ]
            content = message.get("content")
            if content is not None and not isinstance(content, str):
                raise TypeError("LLM content must be a string")
            return LLMResponse(message=message, content=content, tool_calls=tool_calls)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AppError(
                502,
                "llm_invalid_response",
                "The language model returned an invalid response.",
            ) from exc
