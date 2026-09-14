from pydantic import BaseModel, Field


class ToolTraceEvent(BaseModel):
    tool_name: str
    duration_ms: float
    status: str


class AgentTrace(BaseModel):
    run_id: str
    duration_ms: float
    tool_events: list[ToolTraceEvent] = Field(default_factory=list)
