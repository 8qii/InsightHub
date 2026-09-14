# Agent Evaluation and Observability

## Dataset

The deterministic dataset is `evaluation/agent/questions.json`. Each case defines:

- `id` and `question`
- `expected_tools`
- `expected_facts`
- `expected_sources`
- `expected_behavior`, such as `answer`, `clarify`, `abstain`, or `missing_information`
- `should_not_contain`, used for deterministic hallucination checks
- `required_context`, including tool arguments such as historical `as_of_date`

The 21 cases cover normal answers, ambiguous questions, missing information, tool failures, policy conflicts, and citation behavior.

## Metrics

`evaluation/agent/evaluator.py` calculates:

- Tool selection accuracy: exact set match between expected and selected tools.
- Fact match accuracy: deterministic substring match for every expected fact.
- Source match accuracy: deterministic source-title match.
- Context accuracy: deterministic match for required tool arguments.
- Hallucination score: one minus the ratio of forbidden answer phrases found.
- Abstention score: checks for an explicit limitation or clarification when evidence is missing.
- Failure recovery score: checks whether a tool failure was followed by a successful tool result.
- Overall score: the mean of all seven case-level scores.

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
- failure reason and recovered status
- total agent duration

Agent execution is bounded by `AGENT_TIMEOUT_SECONDS`, `AGENT_MAX_ITERATIONS`, and `AGENT_MAX_TOOL_FAILURES`.

Logs include request and run identifiers, selected tools, and timing. Prompts, tool results, document contents, customer data, credentials, and API keys are not logged.
