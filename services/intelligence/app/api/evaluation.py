import importlib
import sys
from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])


class EvaluationRunResponse(BaseModel):
    total_cases: int
    passed: int
    failed: int
    tool_selection_accuracy: float
    fact_match_accuracy: float
    source_match_accuracy: float
    context_accuracy: float
    hallucination_score: float
    abstention_score: float
    clarification_accuracy: float
    failure_recovery_score: float
    overall_score: float


@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(request: Request) -> EvaluationRunResponse:
    repository_path = Path("/app")
    if not (repository_path / "evaluation").exists():
        repository_path = Path(__file__).resolve().parents[4]
    if str(repository_path) not in sys.path:
        sys.path.insert(0, str(repository_path))
    runner = importlib.import_module("evaluation.agent.runner")
    execute_evaluation = runner.run_evaluation

    settings = get_settings()
    report = await execute_evaluation(
        request.app.state.analyst_agent,
        settings.agent_evaluation_dataset_path,
        settings.agent_evaluation_report_path,
    )
    return EvaluationRunResponse(**report.summary.model_dump())
