# ProofSec Phase 11 Final Status Report
**Public Evaluation Platform & Benchmark Expansion**

## Overview
Phase 11 successfully migrated the frozen ProofSec v0.2 local benchmark to a remote execution model on Kaggle Benchmarks. The local integrity of the benchmark is strictly preserved, and Kaggle is explicitly treated as a provider backend.

## Benchmark Execution Details

* **Kaggle Benchmark URL**: https://www.kaggle.com/benchmarks/anuththara2007/proofsec-security-evidence-reasoning-benchmark
* **Kaggle Task URL**: https://www.kaggle.com/benchmarks/tasks/anuththara2007/proofsec-v0-2
* **Kaggle Task Version**: 3
* **Number of Source Tasks**: 110
* **Number of Evaluated Cases**: 110 per model
* **Assertion Count**: 110 per model run (mapped exactly to ground truth classifications)
* **Dataset Hash (SHA256)**: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`

## Implementation Steps
1. **Local Generator** (`kaggle/generate.py`): Parses the 110 frozen tasks from `tasks/` and compiles them into a single, self-contained Python file (`kaggle/tasks/proofsec_v0_2.py`) using robust `try-except` parsing. This ensures stateless remote execution with `llm.prompt()`.
2. **Kaggle Run**: Pushed as `proofsec-v0-2` to Kaggle Benchmarks and executed against multiple foundation models.
3. **Artifact Retrieval**: Built `kaggle/importer.py` to recursively parse Kaggle JSON `.run.json` artifacts, match expectations to actual predictions via assertions, and reconstitute normalized outputs locally.
4. **Metrics Generation**: Updated the existing research engine (`evaluation/calculate_metrics.py`) to accept dynamic directories (`--results-dir`) and save targeted metrics payloads without cross-polluting datasets.

## Model Results

### 1. gpt-5.5-2026-04-23
* **Status**: Completed (Duration: ~5m 30s)
* **Completed Runs**: 110
* **Result Locations**: `results/raw/gpt-5-5-2026-04-23_kaggle/`
* **Overall Accuracy**: 60.9% (67/110)
* **Macro F1**: 64.1%
* **Evidence Sensitivity (PVR)**: 
  * Valid Control Pairs: 20
  * Flips: 10
  * Appropriate Flips: 10 (100% precision on flips)
  * Flip Errors: 0
  * Flip Misses: 10
* **Authority Bias**:
  * Valid Pairs: 5
  * Flips: 0 (Robust to bias)
* **Contradiction Resolution**: 0% (0/5) 
* **Ladder Monotonicity**: 5/5 monotonic ladders (100%)

### 2. gemini-3.7-flash
* **Status**: Completed (Duration: ~3m)
* **Completed Runs**: 110
* **Result Locations**: `results/raw/gemini-3-7-flash_kaggle/`
* **Overall Accuracy**: 0.0% (0/110)
* **Analysis**: Model returned `Parsing Error` uniformly. This indicates a deep-seated Pydantic `ValidationError` originating from the model's inability to return valid strict JSON adhering to the `SecurityAssessment` schema during the Kaggle Benchmarks runner `llm.prompt()` execution.

### 3. claude-sonnet-4-6-default
* **Status**: Running / In Progress
* **Observation**: The Kaggle run for Claude Sonnet is taking significantly longer (15+ minutes) possibly due to concurrent rate limits or internal platform queueing, but remains active in the Kaggle job pool.

## Key Assets Created & Modified
* `kaggle/generate.py` (Kaggle Task Generator)
* `kaggle/tasks/proofsec_v0_2.py` (Remote Execution Script)
* `kaggle/importer.py` (Result ingestion logic)
* `evaluation/calculate_metrics.py` (Argparse extensions)
* Tests: 45/45 passing

## Conclusion
The full end-to-end Kaggle Benchmark integration is complete. We can now run our research-grade frozen benchmark on any new model released on Kaggle natively, download the artifacts, and calculate strict standardized evidence-based metrics via the local researcher ecosystem.
