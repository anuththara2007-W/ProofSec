# ProofSec Researcher Quickstart

## 1. What ProofSec Measures
ProofSec evaluates whether Large Language Models (LLMs) can reliably distinguish *symptoms* of a vulnerability from *proof* of a vulnerability. It measures deductive rigor, specifically detecting "Premature Vulnerability" declarations where models hallucinate exploits based on weak evidence.

## 2. What the Benchmark Contains
- 110 zero-shot, static JSON tasks carefully balanced across One-Fact-Flips, Evidence Ladders, Contradiction tasks, Authority bias, and Terminology bias.
- Located in `tasks/`.

## 3. How the Benchmark is Frozen
- Manifest at `benchmark/manifests/proofsec-v0.2.json` locks the SHA256 dataset hash to exactly `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`.
- The runner automatically intercepts and hashes all 110 tasks prior to injection.

## 4. How to Validate It
Run the integrity checker:
```bash
python evaluation/verify_frozen_benchmark.py
```
This ensures the local tasks match the frozen structural schema exactly.

## 5. How to Run an Evaluation
A fully fresh run against a configured model:
```bash
python scripts/run_benchmark.py --model gemini-3.5-flash --fresh
```

## 6. Where Results are Stored
Raw JSON answers containing latency, tokens, schemas, and timestamps are placed in isolated silos:
```text
results/raw/<model>/
```

## 7. How Metrics are Calculated
Execute the core engine and bootstrap scripts:
```bash
python scratch/upgrade_metrics.py
python evaluation/statistics.py
python evaluation/analyze_surprises.py
```
These populate `results/metrics/`.

## 8. How to Reproduce the Existing Partial Gemini Snapshot
Due to a Kaggle backend HTTP 401 Auth exception during Phase 3, 88 tasks were successfully captured before the token naturally expired. 
To safely process this historical partial snapshot:
```bash
python scripts/run_benchmark.py --model gemini-3.5-flash --resume
```
This will detect the 88 completed files and attempt to fetch the remaining 22 (requires valid Kaggle token).

## 9. Why Multi-Model Results Are Currently Unavailable
The initial research campaign encountered a hard failure on the Kaggle/OpenAI-compatible endpoints (401 Authorization Failed). Under the **Absolute Integrity Rule**, ProofSec never fakes data. Therefore, `gpt-4o` and `claude-3-5-sonnet` remain listed strictly as BLOCKED_EXTERNAL_AUTH until live API communication is restored.
