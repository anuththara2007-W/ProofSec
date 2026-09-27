# ProofSec Phase 11 Final Status Report (Update v2)

## Overview
Phase 11 successfully implemented the Kaggle Benchmark integration. The benchmark correctly runs and evaluates responses without modifying the underlying frozen v0.2 dataset. 

A parser failure affected Gemini 3.7 Flash due to token truncation (`EOF while parsing a string`). The adapter (`kaggle/generate.py`) has been updated to include `max_tokens: 4096` in `extra_api_params` to fix Pydantic schema validation failures.

## Benchmark Metrics

* **Kaggle Task URL**: https://www.kaggle.com/benchmarks/tasks/anuththara2007/proofsec-v0-2/4
* **Dataset Hash (SHA256)**: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`
* **Infrastructure / Parser Failures**: Gemini 3.7 Flash (Version 3) hit 110 parsing errors due to max-token truncation on schema generation. Fully fixed in Version 4 via `max_tokens: 4096`, yielding 0 parser failures.

### 1. claude-sonnet-4-6-default
* **Completed Runs / Evaluated Cases**: 110
* **Result Locations**: `results/raw/claude-sonnet-4-6@default_kaggle/`
* **Metrics Location**: `results/metrics/claude-sonnet-4-6-default_metrics.json`
* **Overall Accuracy**: 72.7% (80/110)
* **Macro F1**: 72.8%

### 2. gpt-5.5-2026-04-23
* **Completed Runs / Evaluated Cases**: 110
* **Result Locations**: `results/raw/gpt-5-5-2026-04-23_kaggle/`
* **Metrics Location**: `results/metrics/gpt-5.5-2026-04-23_metrics.json`
* **Overall Accuracy**: 60.9% (67/110)
* **Macro F1**: 64.1%

### 3. gemini-3.7-flash (Fixed Execution)
* **Completed Runs / Evaluated Cases**: 110
* **Result Locations**: `results/raw/gemini-3-7-flash_kaggle/`
* **Metrics Location**: `results/metrics/gemini-3-7-flash_metrics.json`
* **Overall Accuracy**: 78.2% (86/110)
* **Macro F1**: 78.5%

## Key Assets
* Adapter Tests: `49/49 passing` (`tests/`)
* Modified `kaggle/generate.py` to fix schema serialization truncations.
