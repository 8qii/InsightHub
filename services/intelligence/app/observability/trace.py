import time
from uuid import uuid4

from app.observability.models import AgentTrace, ToolTraceEvent


class TraceRecorder:
    """Collect metadata without storing prompts, results, or tool arguments."""

    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or str(uuid4())
        self._started_at = time.perf_counter()
        self._tool_events: list[ToolTraceEvent] = []

    def record_tool(self, tool_name: str, duration_ms: float, status: str) -> None:
        self._tool_events.append(
            ToolTraceEvent(tool_name=tool_name, duration_ms=duration_ms, status=status)
        )

    def finish(self) -> AgentTrace:
        return AgentTrace(
            run_id=self.run_id,
            duration_ms=round((time.perf_counter() - self._started_at) * 1000, 2),
            tool_events=list(self._tool_events),
        )
