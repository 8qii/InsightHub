# Intelligence Domain Model

## Context

The executive overview and investigation workspace both present business intelligence that must be traceable, display-safe, and stable for the frontend. The domain layer at `services/intelligence/app/domain/intelligence/` owns the shared contracts so future Analyst capabilities use the same vocabulary instead of creating parallel response schemas.

## Shared Contracts

- `Insight`: concise display-safe observation with a title, summary, and metric.
- `Signal`: a detected issue with an ID and severity.
- `Finding`: a validated observation within an investigation.
- `Evidence`: source metadata classified as either a calculated input or supporting context.
- `Investigation`: a curated decision-support package containing findings, drivers, timeline evidence, and suggested questions.

The layer also provides `TimelineEvidence`, `InvestigationDriver`, and `SuggestedQuestion` for the fields required by an investigation. These models intentionally contain no raw database rows, SQL, repository details, or agent internals.

## Signal Lifecycle

```text
Detection
  -> Investigation
  -> Evidence
  -> Analyst
```

1. **Detection**: Overview publishes a `Signal` from deterministic, curated operational metrics.
2. **Investigation**: A signal ID selects a bounded `Investigation` with a conclusion, impact, findings, and drivers.
3. **Evidence**: Each calculation or document reference is represented as `Evidence`; timeline entries add an observation date. `metric_source` identifies calculated input, while `supporting_context` identifies related business context.
4. **Analyst**: Suggested questions are handed to the existing Analyst workflow for broader, traceable follow-up. The domain layer does not alter routing, tools, evaluation, or agent behavior.

## Compatibility

`app.tools.overview.models.PrioritySignal` and `EvidencePreview` remain import-compatible aliases for `Signal` and `Evidence`. Investigation tool models similarly re-export the shared contracts. The API payload fields and frontend behavior remain unchanged.
