# ProofSec Custom Evaluation

**Custom Evaluation API Version:** `1.0`

**Research Benchmark Version:** `v0.2` (frozen, independent)

## Purpose

ProofSec Custom Evaluation allows users to submit their own cybersecurity scenarios and evidence, receiving an evidence-aware security assessment. It brings the research philosophy of ProofSec to user-provided scenarios: **evaluate what the evidence actually proves, not just what it suggests.**

## Research-Data Isolation

Custom evaluations are strictly isolated from the research benchmark:

- Custom evaluations are saved to `custom_evaluations/` only.
- They **never** modify `tasks/`, `results/raw/`, `results/metrics/`, `benchmark/`, or `results/experiments.json`.
- This isolation is verified by automated tests.

## Provider Abstraction

The evaluator is provider-neutral:

```text
CustomEvaluator → ModelProvider → (KaggleProvider | OpenAIProvider | MockProvider)
```

Select a provider via environment variable or CLI flag:

```bash
# Kaggle (default)
python scripts/evaluate.py

# OpenAI-compatible endpoint
PROOFSEC_PROVIDER=openai_compatible PROOFSEC_API_KEY=... python scripts/evaluate.py

# Mock (testing only)
python scripts/evaluate.py --provider mock
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `PROOFSEC_PROVIDER` | Provider backend | `kaggle` |
| `PROOFSEC_MODEL` | Model name | Provider-specific |
| `PROOFSEC_API_KEY` | API key (OpenAI-compatible) | None |
| `PROOFSEC_BASE_URL` | API base URL (OpenAI-compatible) | `https://api.openai.com/v1` |

## CLI Usage

### Interactive mode
```bash
python scripts/evaluate.py
python scripts/evaluate.py --provider openai_compatible
```

### File-based mode
```bash
python scripts/evaluate.py --file request.json
python scripts/evaluate.py --file request.json --provider mock
```

## REST API

```bash
python scripts/api.py
```

### POST /api/v1/evaluate

**Request:**
```json
{
  "scenario": "An API accepts /users/{id}",
  "evidence": ["User IDs are sequential", "Request to /users/1002 returned HTTP 200"],
  "context": "No access control checks observed",
  "question": "Is this vulnerable?",
  "previous_evaluation_id": null
}
```

**Response (200):**
```json
{
  "evaluation_id": "eval-a1b2c3d4e5f6",
  "classification": "Insufficient Evidence",
  "evidence_state": "PARTIAL",
  "supporting_evidence": ["..."],
  "missing_evidence": ["..."],
  "safe_verification": ["..."],
  "impact": "...",
  "reasoning": "..."
}
```

**Error responses:**
| Code | Meaning |
|---|---|
| 400 | Invalid JSON |
| 422 | Schema validation error |
| 429 | Provider rate limited |
| 502 | Provider authentication failure |
| 503 | Provider unavailable |
| 504 | Provider timeout |
| 500 | Internal server error |

Error responses never contain credentials or stack traces.

## Input Schema

```json
{
  "scenario": "string (required)",
  "evidence": ["string"] ,
  "context": "string (optional)",
  "question": "string (optional)",
  "previous_evaluation_id": "string (optional, for revision chains)"
}
```

## Output Schema

```json
{
  "classification": "Vulnerable | Not Vulnerable | Insufficient Evidence",
  "evidence_state": "WEAK | PARTIAL | DECISIVE | CONTRADICTORY | NEGATIVE | UNKNOWN",
  "supporting_evidence": ["string"],
  "missing_evidence": ["string"],
  "safe_verification": ["string"],
  "impact": "string",
  "reasoning": "string"
}
```

## Evidence Revision

ProofSec supports incremental evidence revision:

```text
Evaluation A (eval-abc123)
    ↓ new evidence added
Evaluation B (eval-def456, previous_evaluation_id = eval-abc123)
```

- The original evaluation record is **never** modified.
- Revision chains are tracked via `previous_evaluation_id`.
- Each evaluation receives a unique UUID-based ID.

## Security

- User-provided scenario and evidence are **untrusted input**.
- The prompt template separates system instructions from user data using explicit markers.
- Evaluation IDs are sanitized against path traversal.
- Input size limits prevent abuse.
- Saved records never contain API keys, credentials, or authentication headers.
- Provider failures are never silently converted into security classifications.

## Provider Failure Contract

All providers normalize failures into structured errors:

```text
AUTHENTICATION_ERROR  → HTTP 401/403 at provider
RATE_LIMIT           → HTTP 429 at provider
NETWORK_ERROR        → Connection failure
TIMEOUT              → Request timeout
PROVIDER_UNAVAILABLE → Provider down
PARSER_FAILURE       → Malformed model output
CONFIGURATION_ERROR  → Missing API key or misconfiguration
UNKNOWN_ERROR        → Unexpected failure
```

A provider failure **never** produces a classification result.
