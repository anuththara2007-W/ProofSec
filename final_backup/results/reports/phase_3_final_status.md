# ProofSec Phase 3 Final Status

## Frozen Benchmark
110 zero-shot tasks (Version 0.2).

## Dataset Hash
`422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80` (Verified).

## Dataset Validation
PASS (110 tasks, valid schema, no leakage).

## Models Configured
gemini-3.5-flash, gemini-2.5-pro, claude-3-5-sonnet-20240620, gpt-4o

## Models Actually Evaluated
gemini-3.5-flash

## Complete Experiments
0

## Partial Experiments
- v0_2_gemini-3.5-flash_1727357497 (88/110 tasks completed safely)

## Failed/Blocked Experiments
- gemini-3.5-flash (Tasks 89-110): BLOCKED_EXTERNAL_AUTH
- gemini-2.5-pro: BLOCKED_EXTERNAL_AUTH
- claude-3-5-sonnet-20240620: BLOCKED_EXTERNAL_AUTH
- gpt-4o: BLOCKED_EXTERNAL_AUTH

## Overall Metrics (gemini-3.5-flash partial run)
- Accuracy: 90.91%
- Macro F1: 0.90

## PVR
- 20.45% (Gemini prematurely declared Vulnerability on insufficient evidence in 9/44 eligible cases)

## Evidence Sensitivity
- Evidence Sensitivity: 80.00%
- Appropriate Evidence Sensitivity: 70.00%

## One-Fact-Flip Results
- Flip Miss Rate: 10.00%
- Flip Error Rate: 10.00%
- Pair Consistency: 8/10 matched transitions were successfully executed

## Evidence Ladder Results
- Ladder Monotonicity: 100.00%

## Authority Bias
- Authority Bias Rate: 0.00%

## Terminology Robustness
- Terminology Sensitivity Rate: 0.00%

## Contradiction Resolution
- Contradiction Resolution Accuracy: 100.00%

## Statistical Results
- Bootstrap Confidence Intervals are maintained and recorded.

## Major Findings
Models can achieve high classification accuracy while still demonstrating measurable Premature Vulnerability Rates.

## Failure Analysis
Detailed in `docs/FAILURE_TAXONOMY.md` and `results/reports/surprising_cases.md`. The primary failure mode was PREMATURE_VULNERABILITY overcalling weak symptom presence.

## Infrastructure Issues
`openai.AuthenticationError` (Error code 401) persistently prevents execution across the Kaggle backend. The infrastructure remains strictly BLOCKED. No dummy outputs generated.

## Limitations
Due to the blocked infrastructure, multi-model cross-comparison cannot be generated. External validity is currently limited to the partial Gemini subset.

## Reproducibility
The pipeline is verified end-to-end to correctly maintain isolation, deterministically hash the frozen baseline, and safely resume without overwriting historical datasets.

## Repository State
CLEAN.

## Final Completion Status
PARTIALLY COMPLETE (BLOCKED_EXTERNAL_AUTH)
