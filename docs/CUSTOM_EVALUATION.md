# ProofSec Custom Evaluation

## Purpose
ProofSec provides a Custom Evaluation engine that allows users to submit their own cybersecurity scenarios and evidence, receiving an evidence-aware security assessment. It brings the research philosophy of ProofSec to user-provided scenarios: **evaluate what the evidence actually proves, not just what it suggests.**

## Research-Data Isolation
The Custom Evaluator strictly isolates its operations from the research benchmark dataset.
- Custom evaluations are saved to the `custom_evaluations/` directory.
- It does **not** modify benchmark tasks, metrics, or raw experiment results.
- User data is structurally distinct from the 110-task research footprint.

## Usage (CLI)

An interactive evaluation loop is provided via the CLI:
```bash
python scripts/evaluate.py
```
It will prompt you for:
- **Scenario**: The application context and behavior being tested.
- **Evidence**: Comma-separated list of exact observed facts.
- **Additional context (optional)**: Any other relevant information.

You can also run evaluations non-interactively using a JSON payload:
```bash
python scripts/evaluate.py --file request.json
```

## Input Schema
```json
{
  "scenario": "An API accepts /users/{id}",
  "evidence": ["User IDs are sequential", "My request to /users/1002 returned HTTP 200"],
  "context": "No access control checks were observed",
  "question": "Is this vulnerable?"
}
```

## Output Schema
```json
{
  "classification": "INSUFFICIENT EVIDENCE",
  "evidence_state": "PARTIAL",
  "supporting_evidence": ["..."],
  "missing_evidence": ["..."],
  "safe_verification": ["..."],
  "impact": "...",
  "reasoning": "..."
}
```

## Provider Behavior
The evaluator uses the underlying model provider configured for the repository (e.g. `gemini-3.5-flash` via Kaggle).
If the provider fails or encounters authentication issues (HTTP 401), the evaluation explicitly halts with a failure message. It will **never** fabricate a security classification on infrastructure failure.
