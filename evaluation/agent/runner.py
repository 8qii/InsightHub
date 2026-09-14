from __future__ import annotations

import asyncio
import sys
from pathlib import Path

REPOSITORY_PATH = Path(__file__).resolve().parents[2]
SERVICE_PATH = Path(__file__).resolve().parents[2] / "services" / "intelligence"
if str(REPOSITORY_PATH) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_PATH))
if str(SERVICE_PATH) not in sys.path:
    sys.path.insert(0, str(SERVICE_PATH))

from app.agents.analyst.agent import AnalystAgent  # noqa: E402
from evaluation.agent.evaluator import (  # noqa: E402
    EvaluationReport,
    build_report,
    evaluate_case,
    failed_case,
    load_dataset,
    write_report,
)


async def run_evaluation(
    agent: AnalystAgent, dataset_path: Path, report_path: Path
) -> EvaluationReport:
    cases = load_dataset(dataset_path)
    evaluated = []
    for case in cases:
        try:
            result = await agent.query(case.question, f"evaluation-{case.id}")
            evaluated.append(evaluate_case(case, result))
        except Exception as exc:
            evaluated.append(failed_case(case, type(exc).__name__))
    report = build_report(evaluated)
    write_report(report, report_path)
    return report


async def main() -> None:
    from app.config import get_settings
    from app.main import app

    settings = get_settings()
    async with app.router.lifespan_context(app):
        report = await run_evaluation(
            app.state.analyst_agent,
            settings.agent_evaluation_dataset_path,
            settings.agent_evaluation_report_path,
        )
    print(report.summary.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
