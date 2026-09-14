from threading import Lock

from app.agents.core.models import AgentResult
from app.observability.models import AgentTrace


class AgentRunMetadata:
    def __init__(self, trace: AgentTrace, status: str = "completed") -> None:
        self.run_id = trace.run_id
        self.status = status
        self.duration_ms = trace.duration_ms
        self.tools = [
            {
                "name": event.tool_name,
                "duration_ms": event.duration_ms,
                "status": event.status,
            }
            for event in trace.tool_events
        ]

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "tools": self.tools,
        }


class RunStore:
    """Bounded process-local store for metadata-only agent run inspection."""

    def __init__(self, max_runs: int = 200) -> None:
        self._max_runs = max_runs
        self._runs: dict[str, AgentRunMetadata] = {}
        self._lock = Lock()

    def record(self, result: AgentResult, status: str = "completed") -> None:
        if result.trace is None:
            return
        metadata = AgentRunMetadata(result.trace, status)
        with self._lock:
            self._runs[metadata.run_id] = metadata
            while len(self._runs) > self._max_runs:
                self._runs.pop(next(iter(self._runs)))

    def get(self, run_id: str) -> AgentRunMetadata | None:
        with self._lock:
            return self._runs.get(run_id)


default_run_store = RunStore()
