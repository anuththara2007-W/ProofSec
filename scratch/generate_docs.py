import os

docs = {
    "docs/ARCHITECTURE.md": """# ProofSec Architecture
- **src/proofsec/**: Core logic (schema, runner).
- **tasks/**: JSON task definitions separated from execution code.
- **experiments/**: Configs linking task IDs to experiments.
- **results/**: Immutable raw LLM outputs, metrics, and reports.
- **benchmark/**: Kaggle interface (`kaggle_benchmark.py`).
- **evaluation/**: Validation, metrics, and visualization scripts.
- **scripts/**: CLI entry points.
""",
    "docs/TAXONOMY.md": """# Task Taxonomy
## Domains
IDOR, Authentication, SSRF, SQLi, Business Logic, Rate Limiting, JWT, Info Disclosure, Headers.

## Evidence States
- **WEAK**: Missing context/proof.
- **PARTIAL**: Strong signal, still unproven.
- **DECISIVE**: Confirmed vulnerability.
- **CONTRADICTORY**: Conflicting logs/claims.
- **NEGATIVE**: Benign context confirmed.

## Reasoning Phenomena
False Positives, False Negatives, Contradictions, Authority Bias, Terminology Traps.
""",
    "docs/EXPERIMENTS.md": """# Ablation & Experiments
- **Evidence Ladders**: Gradual injection of stronger evidence.
- **One-Fact-Flip Pairs**: Control exactly one variable (e.g. `owner_id = me` vs `owner_id = you`).
- **Contradiction Resolution**: Introduce contradicting facts.
- **Authority Bias**: Inject fake expert claims.
""",
    "docs/PROOF_THRESHOLD.md": """# Proof Threshold Concept
ProofSec evaluates whether models recognize when available evidence crosses the threshold required to justify a security conclusion. We distinguish "possible signal" from "demonstrated vulnerability".
""",
    "docs/RESEARCH_STORY.md": """# Research Story
Traditional security benchmarks often ask whether a model can recognize a vulnerability pattern.
ProofSec asks a harder question: **Does the model know when it has enough evidence to make that claim?**
""",
    "docs/LIMITATIONS.md": """# Limitations
- Scenarios are synthetic and isolated.
- Model proxy differences may exist.
- Single-turn architecture limits real interactive verification.
- Not a substitute for real telemetry or production testing.
""",
    "docs/STATUS.md": """# Status Report
- Version: 0.1.0
- Tasks: 30
- Categories: 10
- Models: gemini-3.5-flash
- Validation: PASS
- Next Milestone: v0.2 (100 tasks)
""",
    "ROADMAP.md": """# Roadmap
- **v0.1**: 30-task calibration set.
- **v0.2**: 100-task research dataset.
- **v0.3**: Multi-model evaluation.
- **v0.4**: Counterfactual/evidence-ladder expansion.
- **v0.5**: Statistical evaluation.
- **v1.0**: Large-scale benchmark.
"""
}

for path, content in docs.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
print("Docs generated.")
