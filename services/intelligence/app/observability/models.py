from pydantic import BaseModel, Field


class ToolTraceEvent(BaseModel):
    tool_name: str
    duration_ms: float
    status: str
    failure_reason: str | None = None


class AgentTrace(BaseModel):
    run_id: str
    duration_ms: float
    tool_events: list[ToolTraceEvent] = Field(default_factory=list)
    failure_reason: str | None = None
    recovered: bool = False
