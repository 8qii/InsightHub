# ruff: noqa: E402

import asyncio
import json
import logging
import sys
from pathlib import Path

REPOSITORY_PATH = Path(__file__).resolve().parents[3]
if str(REPOSITORY_PATH) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_PATH))

from evaluation.agent.evaluator import (
    EvaluationCase,
    evaluate_case,
    load_dataset,
    summarize,
)  # noqa: E402

from app.agents.core.models import AgentResult  # noqa: E402
from app.api.evaluation import EvaluationRunResponse  # noqa: E402
from app.logging import JsonFormatter  # noqa: E402
from app.observability.trace import TraceRecorder  # noqa: E402

DATASET_PATH = Path(__file__).resolve().parents[3] / "evaluation" / "agent" / "questions.json"


def test_dataset_loads_required_cases() -> None:
    cases = load_dataset(DATASET_PATH)

    assert len(cases) == 4
    assert {case.id for case in cases} == {
        "vip-discount-policy",
        "discount-violations",
        "luna-q3-analysis",
        "historical-inventory-analysis",
    }


def test_evaluator_matches_tools_facts_sources_and_context() -> None:
    case = EvaluationCase(
        id="historical",
        question="Historical inventory",
        expected_tools=["get_inventory_risk"],
        expected_facts=["138 days"],
        expected_sources=[],
        required_context={
            "tool_arguments": {
                "get_inventory_risk": {
                    "age_threshold_days": 90,
                    "as_of_date": "2025-09-30",
                }
            }
        },
    )
    result = AgentResult(
        answer="Product Luna inventory was 138 days old.",
        sources=[],
        selected_tools=["get_inventory_risk"],
        iterations=2,
        tool_calls=[
            {
                "name": "get_inventory_risk",
                "arguments": {"age_threshold_days": 90, "as_of_date": "2025-09-30"},
            }
        ],
    )

    evaluation = evaluate_case(case, result)

    assert evaluation.passed is True
    assert evaluation.context_score == 1


def test_evaluator_summary_counts_failures() -> None:
    case = EvaluationCase(
        id="case",
        question="Question",
        expected_tools=[],
        expected_facts=[],
        expected_sources=[],
    )
    passed = evaluate_case(
        case,
        AgentResult(answer="answer", sources=[], selected_tools=[], iterations=1),
    )
    failed = passed.model_copy(update={"passed": False, "score": 0})

    summary = summarize([passed, failed])

    assert summary.total_cases == 2
    assert summary.passed == 1
    assert summary.failed == 1


def test_trace_records_timing_and_status_without_content() -> None:
    trace = TraceRecorder("run-test")
    trace.record_tool("get_inventory_risk", 4.2, "success")

    payload = json.loads(trace.finish().model_dump_json())

    assert payload["run_id"] == "run-test"
    assert payload["tool_events"] == [
        {"tool_name": "get_inventory_risk", "duration_ms": 4.2, "status": "success"}
    ]
    assert "answer" not in json.dumps(payload)


def test_evaluation_runner_writes_report(tmp_path: Path) -> None:
    from evaluation.agent.runner import run_evaluation

    dataset = tmp_path / "questions.json"
    report = tmp_path / "latest.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "id": "one",
                    "question": "Question",
                    "expected_tools": [],
                    "expected_facts": ["answer"],
                    "expected_sources": [],
                    "required_context": {},
                }
            ]
        ),
        encoding="utf-8",
    )

    class FakeAgent:
        async def query(self, question: str, request_id: str) -> AgentResult:
            return AgentResult(answer="answer", sources=[], selected_tools=[], iterations=1)

    result = asyncio.run(run_evaluation(FakeAgent(), dataset, report))

    assert result.summary.passed == 1
    assert report.exists()


def test_evaluation_response_schema_contains_summary() -> None:
    response = EvaluationRunResponse(
        total_cases=1,
        passed=1,
        failed=0,
        tool_selection_accuracy=1,
        fact_match_accuracy=1,
        source_match_accuracy=1,
        context_accuracy=1,
        overall_score=1,
    )

    assert response.overall_score == 1


def test_json_logs_filter_secrets_and_content() -> None:
    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "completed", (), None)
    record.api_key = "secret-api-key"
    record.document_content = "private document"
    record.run_id = "run-test"

    output = JsonFormatter().format(record)

    assert "secret-api-key" not in output
    assert "private document" not in output
    assert "run-test" in output
