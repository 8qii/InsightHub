import asyncio
import json
import logging
import time
from typing import Any

from pydantic import ValidationError

from app.agents.core.models import ToolContext, ToolExecutionResult
from app.agents.core.registry import ToolRegistry
from app.errors import AppError
from app.observability.trace import TraceRecorder

logger = logging.getLogger("insighthub.agent")


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        timeout_seconds: float,
        trace: TraceRecorder | None = None,
    ) -> None:
        self._registry = registry
        self._timeout_seconds = timeout_seconds
        self._trace = trace

    async def execute(
        self,
        name: str,
        raw_arguments: str,
        context: ToolContext,
    ) -> ToolExecutionResult:
        started_at = time.perf_counter()
        definition = self._registry.get(name)
        if definition is None:
            result = ToolExecutionResult(ok=False, error=f"Unknown tool: {name}")
            if self._trace is not None:
                self._trace.record_tool(
                    name,
                    round((time.perf_counter() - started_at) * 1000, 2),
                    "error",
                )
            return result

        try:
            arguments = definition.input_schema.model_validate(json.loads(raw_arguments))
            result = await asyncio.wait_for(
                definition.execute(arguments, context), timeout=self._timeout_seconds
            )
            tool_result = ToolExecutionResult(ok=True, data=_serialize(result))
        except (json.JSONDecodeError, ValidationError) as exc:
            tool_result = ToolExecutionResult(ok=False, error="Invalid tool arguments.")
            logger.info(
                "Agent tool argument validation failed",
                extra={"request_id": context.request_id, "tool_name": name},
            )
            _ = exc
        except TimeoutError:
            tool_result = ToolExecutionResult(ok=False, error="The tool timed out.")
        except AppError as exc:
            tool_result = ToolExecutionResult(ok=False, error=exc.message)
        except Exception:
            logger.exception(
                "Agent tool execution failed",
                extra={"request_id": context.request_id, "tool_name": name},
            )
            tool_result = ToolExecutionResult(ok=False, error="The tool failed safely.")

        logger.info(
            "Agent tool completed",
            extra={
                "tool_name": name,
                "request_id": context.request_id,
                "run_id": context.run_id,
                "tool_duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                "result_status": "success" if tool_result.ok else "error",
            },
        )
        if self._trace is not None:
            self._trace.record_tool(
                name,
                round((time.perf_counter() - started_at) * 1000, 2),
                "success" if tool_result.ok else "error",
            )
        return tool_result


def _serialize(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value
