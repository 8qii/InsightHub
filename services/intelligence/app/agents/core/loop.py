import json
import logging
import time
from typing import Any

from app.agents.core.executor import ToolExecutor
from app.agents.core.llm import OpenAICompatibleClient
from app.agents.core.models import AgentResult, ToolContext
from app.agents.core.registry import ToolRegistry
from app.errors import AppError

logger = logging.getLogger("insighthub.agent")


class AgentLoop:
    def __init__(
        self,
        llm: OpenAICompatibleClient,
        registry: ToolRegistry,
        tool_timeout_seconds: float,
        max_iterations: int,
    ) -> None:
        self._llm = llm
        self._registry = registry
        self._executor = ToolExecutor(registry, tool_timeout_seconds)
        self._max_iterations = max_iterations

    async def run(self, question: str, request_id: str, system_prompt: str) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        selected_tools: list[str] = []
        sources: list[Any] = []
        context = ToolContext(request_id=request_id)
        started_at = time.perf_counter()

        for iteration in range(1, self._max_iterations + 1):
            response = await self._llm.complete(messages, self._registry.as_openai_tools())
            if not response.tool_calls:
                if not response.content or not response.content.strip():
                    raise AppError(502, "agent_empty_answer", "The agent returned an empty answer.")
                self._log_completion(request_id, selected_tools, started_at, iteration)
                return AgentResult(
                    answer=response.content.strip(),
                    sources=sources,
                    selected_tools=selected_tools,
                    iterations=iteration,
                )

            messages.append(response.message)
            for tool_call in response.tool_calls:
                selected_tools.append(tool_call.name)
                result = await self._executor.execute(tool_call.name, tool_call.arguments, context)
                if isinstance(result.data, dict) and isinstance(result.data.get("sources"), list):
                    sources.extend(result.data["sources"])
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.call_id,
                        "content": json.dumps(result.model_dump(mode="json")),
                    }
                )

        raise AppError(504, "agent_iteration_limit", "The agent exceeded its tool-call limit.")

    @staticmethod
    def _log_completion(
        request_id: str, selected_tools: list[str], started_at: float, iteration: int
    ) -> None:
        logger.info(
            "Agent query completed",
            extra={
                "request_id": request_id,
                "selected_tools": selected_tools,
                "iteration": iteration,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                "result_status": "success",
            },
        )
