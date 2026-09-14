from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.observability.models import AgentTrace


@dataclass(frozen=True)
class ToolContext:
    request_id: str
    run_id: str = ""
    default_tool_arguments: dict[str, dict[str, Any]] = field(default_factory=dict)


ToolCallable = Callable[[BaseModel, ToolContext], Awaitable[Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: type[BaseModel]
    execute: ToolCallable

    def as_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema.model_json_schema(),
            },
        }


@dataclass(frozen=True)
class LLMToolCall:
    call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class LLMResponse:
    message: dict[str, Any]
    content: str | None
    tool_calls: list[LLMToolCall]


class ToolResult(BaseModel):
    ok: bool
    status: Literal["success", "error"]
    data: Any = None
    error: str | None = None
    error_code: str | None = None


# Kept as a local alias for callers from the Phase 5 contract.
ToolExecutionResult = ToolResult


class AgentResult(BaseModel):
    answer: str
    sources: list[Any]
    selected_tools: list[str]
    iterations: int
    run_id: str = ""
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    trace: AgentTrace | None = None
