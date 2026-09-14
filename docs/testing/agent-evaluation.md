# Agent Evaluation and Observability

## Dataset

The deterministic dataset is `evaluation/agent/questions.json`. Each case defines:

- `id` and `question`
- `expected_tools`
- `expected_facts`
- `expected_sources`
- `required_context`, including tool arguments such as historical `as_of_date`

The cases cover policy retrieval, discount violations, Product Luna's Q3 analysis, and historical inventory analysis.

## Metrics

`evaluation/agent/evaluator.py` calculates:

- Tool selection accuracy: exact set match between expected and selected tools.
- Fact match accuracy: deterministic substring match for every expected fact.
- Source match accuracy: deterministic source-title match.
- Context accuracy: deterministic match for required tool arguments.
- Overall score: the mean of the four case-level scores.

No LLM judge is used.

## Execution

Run the real configured agent from the repository root:

```powershell
python evaluation/agent/runner.py
```

The runner loads the dataset, executes each question, evaluates the result, and writes `evaluation/agent/reports/latest.json`.

The same operation is available through the internal endpoint:

```text
POST /api/v1/evaluation/run
```

The Docker Compose service mounts the evaluation directory so the report is retained in the workspace.

## Observability

Each agent query receives a `run_id`. Internal traces contain only:

- tool name
- execution duration
- success/error status
- total agent duration

Logs include request and run identifiers, selected tools, and timing. Prompts, tool results, document contents, customer data, credentials, and API keys are not logged.
