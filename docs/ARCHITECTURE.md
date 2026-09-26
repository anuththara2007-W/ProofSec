# ProofSec Architecture

## Overview

ProofSec is a research benchmark and evaluation platform for **evidence-grounded security reasoning** in AI models. The project is divided into two strictly separated domains:

```text
                    PROOFSEC
                       │
          ┌────────────┴────────────┐
          │                         │
       RESEARCH                  PRODUCT
          │                         │
  Frozen benchmark             Custom input
  110 tasks                    User evidence
  Experiments                  Evaluation
  Metrics                      API / CLI
  Statistics                   Provider abstraction
          │                         │
          └────────────┬────────────┘
                       │
                Shared evaluation
                    principles
```

> **Research benchmark execution and custom user evaluations are separate data domains.**

## Research Domain

The research benchmark answers:

> "Does an AI model change its security judgment appropriately when evidence changes?"

### Components

```text
tasks/                     → 110 frozen JSON benchmark tasks
benchmark/manifests/       → Frozen manifest (proofsec-v0.2.json)
evaluation/                → Metric recomputation, dataset validation
results/raw/               → Immutable historical model responses
results/metrics/           → Computed metrics (accuracy, PVR, flip rates, etc.)
results/experiments.json   → Experiment registry
src/proofsec/runner.py     → Research benchmark runner (Kaggle integration)
```

### Invariants

- Benchmark version: `v0.2`
- Task count: `110`
- Dataset SHA256: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`
- Historical metrics are never modified by product operations.

## Product Domain

The product answers:

> "Given this scenario and evidence, what does the evidence actually establish?"

### Architecture

```text
User Input (CLI / API / SDK)
       ↓
CustomEvaluator
       ↓
ModelProvider (abstract interface)
       ↓
┌──────────────┬───────────────┬──────────────┐
│ KaggleProvider│ OpenAIProvider │ MockProvider │
│ (kaggle_bench)│ (/v1/chat/...)│ (tests only) │
└──────────────┴───────────────┴──────────────┘
```

### Components

```text
src/proofsec/schemas.py     → Input/output schemas, version constant
src/proofsec/providers.py   → ModelProvider ABC, KaggleProvider, OpenAIProvider, MockProvider
src/proofsec/evaluator.py   → CustomEvaluator (provider-neutral evaluation engine)
scripts/evaluate.py         → CLI interface
scripts/api.py              → Local REST API (POST /api/v1/evaluate)
custom_evaluations/         → Saved evaluation records (never in results/)
```

### Provider Contract

All providers normalize responses into `ProviderResponse(status, result, error_message)`.

Failure statuses:
```text
AUTHENTICATION_ERROR
RATE_LIMIT
NETWORK_ERROR
TIMEOUT
PROVIDER_UNAVAILABLE
PARSER_FAILURE
CONFIGURATION_ERROR
UNKNOWN_ERROR
```

A provider failure **never** produces a classification. It always produces a structured error.

### Health Check Contract

Every provider exposes `health_check() → HealthStatus(provider, model, status)`.

Possible statuses: `AVAILABLE`, `AUTHENTICATION_ERROR`, `PROVIDER_UNAVAILABLE`, `NETWORK_ERROR`, `CONFIGURATION_ERROR`, `UNKNOWN`.

Health checks never submit benchmark tasks or modify research data.

### Evidence Revision

Custom evaluations support revision chains:

```text
Evaluation A (eval-abc123)
    ↓ new evidence added
Evaluation B (eval-def456, previous_evaluation_id=eval-abc123)
```

The original evaluation record is never modified.

### Security Boundaries

- User-provided scenario/evidence is treated as **untrusted input**.
- The prompt template separates `SYSTEM/DEVELOPER EVALUATION INSTRUCTIONS` from `USER-PROVIDED` sections.
- Evaluation IDs are sanitized against path traversal.
- Saved records never contain credentials, API keys, or authentication headers.
- Input size limits prevent abuse.

## File Isolation Matrix

| Directory | Research | Product |
|---|---|---|
| `tasks/` | ✅ Read | ❌ Never written |
| `results/raw/` | ✅ Read/Write | ❌ Never touched |
| `results/metrics/` | ✅ Write | ❌ Never touched |
| `benchmark/` | ✅ Read | ❌ Never touched |
| `custom_evaluations/` | ❌ Never touched | ✅ Write |
