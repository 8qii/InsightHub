import asyncio
import json
import logging
import time
from typing import Any

from app.agents.core.executor import ToolExecutor
from app.agents.core.llm import OpenAICompatibleClient
from app.agents.core.models import AgentResult, ToolContext
from app.agents.core.registry import ToolRegistry
from app.errors import AppError
from app.observability.trace import TraceRecorder

logger = logging.getLogger("insighthub.agent")


class AgentLoop:
    def __init__(
        self,
        llm: OpenAICompatibleClient,
        registry: ToolRegistry,
        tool_timeout_seconds: float,
        max_iterations: int,
        max_tool_failures: int = 2,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._llm = llm
        self._registry = registry
        self._tool_timeout_seconds = tool_timeout_seconds
        self._max_iterations = max_iterations
        self._max_tool_failures = max_tool_failures
        self._timeout_seconds = timeout_seconds

    async def run(
        self,
        question: str,
        request_id: str,
        system_prompt: str,
        run_id: str | None = None,
        default_tool_arguments: dict[str, dict[str, Any]] | None = None,
    ) -> AgentResult:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                return await self._run(
                    question,
                    request_id,
                    system_prompt,
                    run_id,
                    default_tool_arguments,
                )
        except TimeoutError as exc:
            raise AppError(504, "agent_timeout", "The agent timed out safely.") from exc

    async def _run(
        self,
        question: str,
        request_id: str,
        system_prompt: str,
        run_id: str | None = None,
        default_tool_arguments: dict[str, dict[str, Any]] | None = None,
    ) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        selected_tools: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        sources: list[Any] = []
        tool_failure_count = 0
        failure_reason: str | None = None
        recovered = False
        started_at = time.perf_counter()
        trace = TraceRecorder(run_id)
        context = ToolContext(
            request_id=request_id,
            run_id=trace.run_id,
            default_tool_arguments=default_tool_arguments or {},
        )
        executor = ToolExecutor(self._registry, self._tool_timeout_seconds, trace)

        for iteration in range(1, self._max_iterations + 1):
            response = await self._llm.complete(messages, self._registry.as_openai_tools())
            if not response.tool_calls:
                if not response.content or not response.content.strip():
                    raise AppError(502, "agent_empty_answer", "The agent returned an empty answer.")
                self._log_completion(
                    request_id, trace.run_id, selected_tools, started_at, iteration
                )
                return AgentResult(
                    answer=response.content.strip(),
                    sources=sources,
                    selected_tools=selected_tools,
                    iterations=iteration,
                    run_id=trace.run_id,
                    tool_calls=tool_calls,
                    trace=trace.finish(failure_reason, recovered or bool(failure_reason)),
                )

            messages.append(response.message)
            for tool_call in response.tool_calls:
                selected_tools.append(tool_call.name)
                tool_calls.append(
                    {
                        "name": tool_call.name,
                        "arguments": _normalized_arguments(
                            self._registry,
                            tool_call.name,
                            _apply_default_arguments(
                                tool_call.name, tool_call.arguments, context
                            ),
                        ),
                    }
                )
                result = await executor.execute(
                    tool_call.name,
                    _apply_default_arguments(tool_call.name, tool_call.arguments, context),
                    context,
                )
                if not result.ok:
                    tool_failure_count += 1
                    failure_reason = result.error_code or result.error
                    if tool_failure_count > self._max_tool_failures:
                        raise AppError(
                            502,
                            "agent_tool_failure_limit",
                            "The agent exceeded its tool failure limit.",
                        )
                elif tool_failure_count:
                    recovered = True
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
        request_id: str,
        run_id: str,
        selected_tools: list[str],
        started_at: float,
        iteration: int,
    ) -> None:
        logger.info(
            "Agent query completed",
            extra={
                "request_id": request_id,
                "run_id": run_id,
                "selected_tools": selected_tools,
                "iteration": iteration,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                "result_status": "success",
            },
        )


def _normalized_arguments(
    registry: ToolRegistry, name: str, raw_arguments: str
) -> dict[str, Any]:
    definition = registry.get(name)
    if definition is None:
        return {}
    try:
        return definition.input_schema.model_validate_json(raw_arguments).model_dump(mode="json")
    except (TypeError, ValueError):
        return {}


def _apply_default_arguments(name: str, raw_arguments: str, context: ToolContext) -> str:
    defaults = context.default_tool_arguments.get(name)
    if not defaults:
        return raw_arguments
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return raw_arguments
    if not isinstance(arguments, dict):
        return raw_arguments
    for key, value in defaults.items():
        arguments.setdefault(key, value)
    return json.dumps(arguments)
