from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_tools: list[str]
    expected_facts: list[str]
    expected_sources: list[str]
    required_context: dict[str, Any] = Field(default_factory=dict)


class CaseEvaluation(BaseModel):
    id: str
    passed: bool
    score: float
    tool_selection_score: float
    fact_score: float
    source_score: float
    context_score: float
    selected_tools: list[str]
    matched_facts: list[str]
    matched_sources: list[str]
    context_matches: list[str]
    answer_sha256: str
    error: str | None = None


class EvaluationSummary(BaseModel):
    total_cases: int
    passed: int
    failed: int
    tool_selection_accuracy: float
    fact_match_accuracy: float
    source_match_accuracy: float
    context_accuracy: float
    overall_score: float


class EvaluationReport(BaseModel):
    generated_at: datetime
    summary: EvaluationSummary
    cases: list[CaseEvaluation]


def load_dataset(path: Path) -> list[EvaluationCase]:
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Evaluation dataset must be a JSON array")
    return [EvaluationCase.model_validate(item) for item in payload]


def evaluate_case(case: EvaluationCase, result: Any) -> CaseEvaluation:
    answer = str(getattr(result, "answer", ""))
    selected_tools = list(getattr(result, "selected_tools", []))
    source_titles = {
        str(source.get("title", "")).casefold()
        for source in getattr(result, "sources", [])
        if isinstance(source, dict)
    }
    matched_facts = [fact for fact in case.expected_facts if _contains(answer, fact)]
    matched_sources = [
        source for source in case.expected_sources if source.casefold() in source_titles
    ]
    context_matches = _match_context(case.required_context, getattr(result, "tool_calls", []))
    tool_score = float(set(selected_tools) == set(case.expected_tools))
    fact_score = _ratio(len(matched_facts), len(case.expected_facts))
    source_score = _ratio(len(matched_sources), len(case.expected_sources))
    context_expected = _expected_context_count(case.required_context)
    context_score = _ratio(len(context_matches), context_expected)
    score = round((tool_score + fact_score + source_score + context_score) / 4, 4)
    return CaseEvaluation(
        id=case.id,
        passed=(tool_score == 1 and fact_score == 1 and source_score == 1 and context_score == 1),
        score=score,
        tool_selection_score=tool_score,
        fact_score=fact_score,
        source_score=source_score,
        context_score=context_score,
        selected_tools=selected_tools,
        matched_facts=matched_facts,
        matched_sources=matched_sources,
        context_matches=context_matches,
        answer_sha256=hashlib.sha256(answer.encode("utf-8")).hexdigest(),
    )


def failed_case(case: EvaluationCase, error: str) -> CaseEvaluation:
    return CaseEvaluation(
        id=case.id,
        passed=False,
        score=0,
        tool_selection_score=0,
        fact_score=0,
        source_score=0,
        context_score=0,
        selected_tools=[],
        matched_facts=[],
        matched_sources=[],
        context_matches=[],
        answer_sha256="",
        error=error,
    )


def summarize(cases: list[CaseEvaluation]) -> EvaluationSummary:
    total = len(cases)
    return EvaluationSummary(
        total_cases=total,
        passed=sum(case.passed for case in cases),
        failed=sum(not case.passed for case in cases),
        tool_selection_accuracy=_average(case.tool_selection_score for case in cases),
        fact_match_accuracy=_average(case.fact_score for case in cases),
        source_match_accuracy=_average(case.source_score for case in cases),
        context_accuracy=_average(case.context_score for case in cases),
        overall_score=_average(case.score for case in cases),
    )


def build_report(cases: list[CaseEvaluation]) -> EvaluationReport:
    return EvaluationReport(
        generated_at=datetime.now(timezone.utc), summary=summarize(cases), cases=cases
    )


def write_report(report: EvaluationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def _contains(answer: str, fact: str) -> bool:
    return re.sub(r"\s+", " ", fact.casefold()) in re.sub(r"\s+", " ", answer.casefold())


def _ratio(matched: int, expected: int) -> float:
    return 1.0 if expected == 0 else round(matched / expected, 4)


def _expected_context_count(context: dict[str, Any]) -> int:
    return sum(len(arguments) for arguments in context.get("tool_arguments", {}).values())


def _match_context(context: dict[str, Any], tool_calls: list[dict[str, Any]]) -> list[str]:
    matches: list[str] = []
    for tool_name, expected_arguments in context.get("tool_arguments", {}).items():
        for call in tool_calls:
            if call.get("name") != tool_name:
                continue
            actual = call.get("arguments", {})
            for key, value in expected_arguments.items():
                if actual.get(key) == value:
                    matches.append(f"{tool_name}.{key}")
            break
    return matches


def _average(values: Any) -> float:
    values = list(values)
    return round(sum(values) / len(values), 4) if values else 0.0
