# ProofSec

ProofSec is an evidence-grounded AI evaluation framework and security reasoning benchmark. It goes beyond simple multiple-choice questions or unstructured text generation by requiring Large Language Models (LLMs) to substantiate their security claims with concrete, verifiable evidence.

## What problem does it solve?
Ordinary LLM benchmarks for cybersecurity often suffer from:
- **Guessing**: Models can guess the right answer without understanding the logic.
- **Hallucination**: Models claim a vulnerability exists without proof.
- **Authority Bias**: Models defer to human statements rather than evaluating the raw technical facts.

ProofSec solves this by enforcing an **evidence-state** evaluation (e.g., Decisive, Partial, Insufficient, Contradictory) alongside the classification (Vulnerable / Not Vulnerable).

## Frozen Benchmark vs User Evaluations
ProofSec is designed with two distinct operational modes that are strictly isolated:
- **Frozen Benchmark (v0.2)**: A scientifically rigorous, immutably hashed dataset of 110 tasks used for standardized researcher evaluation.
- **Custom User Evaluations**: Developer-driven custom scenarios evaluated safely without polluting or altering the historical research benchmark.

## Quick Start

### Local Installation
Requires Python 3.9+
```bash
pip install -r requirements.txt
pip install -e .
```

### Running with Docker
```bash
docker build -t proofsec .
docker run -p 8000:8000 proofsec
```
Or using docker-compose:
```bash
docker-compose up -d
```
Access the web dashboard at `http://localhost:8000`.

## Developer SDK
```python
from proofsec import ProofSec

client = ProofSec(provider="openai_compatible")
result = client.evaluate(
    scenario="User input is concatenated into SQL query.",
    evidence=["Input is unsanitized", "Database returns syntax error on quote"]
)
print(result.classification)
```

## Researcher Mode
To analyze the frozen benchmark:
```bash
proofsec benchmark status
proofsec benchmark hash
proofsec research metrics
```

## Adding a Provider
New providers can be added in `src/proofsec/providers.py` by implementing the `ModelProvider` interface. See `docs/PROVIDERS.md` for details.
