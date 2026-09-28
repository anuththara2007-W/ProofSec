# ProofSec Phase 11: Public Evaluation Platform & Benchmark Expansion

## 1. Overview
Phase 11 achieves two primary objectives: transitioning the product into a public-ready evaluation ecosystem (Track A) and laying the scientific foundation for the v0.3 research benchmark (Track B). Strict data integrity rules were upheld throughout, with no fabrication of data and perfect preservation of the v0.2 benchmark.

## 2. Track A: Public Product
- **Evaluation Workflow & Revisions**: Expanded the CustomEvaluator to support rigorous, non-destructive revisions. The UI now tracks revisions effectively over time as a timeline.
- **Compare Engine**: Implemented `CompareEngine` (`src/proofsec/compare.py`) to systematically analyze state transitions between revisions without asserting ground-truth "accuracy".
- **User-Provided Ground Truth**: Upgraded schemas to accept `expected_classification`, `expected_evidence_state`, and `expected_decisive_fact`. These strictly bypass the model prompt to prevent data leakage.
- **Custom Metrics**: When ground truth is available, the Compare Engine automatically calculates `classification_correct` and `evidence_state_correct`. If absent, it gracefully reports "Ground truth not provided".
- **Storage Abstraction**: Created `EvaluationStore` (and `FileEvaluationStore`) in `src/proofsec/storage.py` to abstract the persistence layer away from local files, allowing future SQL implementations.
- **API Hardening**: `ProofSecAPIHandler` now features an authentication middleware abstraction ready for configurable API Key enforcement. The API surfaces endpoints for `/evaluate`, `/evaluations/{id}/compare`, and historical retrieval.
- **Web Dashboard**: Upgraded to a complete Single Page Application (SPA) with views for Workspace, Revisions, Timeline, Benchmark, Research, and Documentation.

## 3. Track B: Benchmark Research
- **ProofSec v0.3 Architecture**: Created `benchmark/manifests/proofsec-v0.3.json` and established the `tasks/v0.3/` namespace.
- **One-Fact-Flip Quality Control**: Created an automated `OneFactFlipValidator` (`src/proofsec/research/validator.py`) and schema to enforce pair integrity (preventing unintended fact bleed).
- **Advanced Methodologies Prepared**: Documented Evidence Ladders, Contradictory Evidence, and Temporal Reasoning in `PROOFSEC_V03_PROTOCOL.md`.
- **Experiment Replay**: Implemented `proofsec research replay <id>` in the CLI to allow deterministic re-analysis of partial experiments.
- **New Documentation**: Created `PROOFSEC_V03_PROTOCOL.md`, `PROOFSEC_V03_CARD.md`, and `EVALUATION_GUIDE.md`.

## 4. Integrity and Security Checks
- **v0.2 Hash Before**: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`
- **v0.2 Hash After**: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`
- **Historical Metrics**: Verified untouched (Accuracy: 65.91%). No MockProvider output polluted the historical run.
- **Total Tests Passing**: 48/48 (Added tests for storage abstraction, comparison engine, and research features).
- **Secrets Audit**: Clean. No keys leaked in codebase.
- **Mock Results**: None generated for official metrics.
- **Docker Status**: Ready (carried over from Phase 10).
- **Package Installation**: Functional via standard `pip install -e .`.

## 5. Known Limitations & Next Steps
- Inter-annotator agreement functions (Cohen's Kappa) require multiple annotators which do not yet exist; the framework is laid out in the documentation.
- The `v0.3` benchmark is currently a skeleton with an example pair (`task-1a.json` and `task-1b.json`) for validation testing; the full dataset remains to be authored.
- The Kaggle provider remains constrained by external HTTP 401 blocks. Live re-evaluations require alternative credentials.

## 6. Exact Commands for Verification
```bash
# Verify integrity
proofsec benchmark hash

# Run tests
python -m unittest discover tests

# Replay experiment configuration
proofsec research replay v0_2_gemini-3.5-flash_1727357497

# Start platform
proofsec serve --port 8000
```
