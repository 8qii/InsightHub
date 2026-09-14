from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolContext:
    request_id: str


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


class ToolExecutionResult(BaseModel):
    ok: bool
    data: Any = None
    error: str | None = None


class AgentResult(BaseModel):
    answer: str
    sources: list[Any]
    selected_tools: list[str]
    iterations: int
