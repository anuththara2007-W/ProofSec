# ProofSec Architecture
- **src/proofsec/**: Core logic (schema, runner).
- **tasks/**: JSON task definitions separated from execution code.
- **experiments/**: Configs linking task IDs to experiments.
- **results/**: Immutable raw LLM outputs, metrics, and reports.
- **benchmark/**: Kaggle interface (`kaggle_benchmark.py`).
- **evaluation/**: Validation, metrics, and visualization scripts.
- **scripts/**: CLI entry points.
