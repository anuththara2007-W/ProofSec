# Phase 3 Status

## Frozen Benchmark
ProofSec v0.2 verified against SHA256 manifest.

## Models Configured
gemini-3.5-flash, gemini-2.5-pro, claude-3-5-sonnet-20240620, gpt-4o

## Models Actually Evaluated
gemini-3.5-flash (Partial Run preserved)

## Completed Experiments
None

## Partial Experiments
v0_2_gemini-3.5-flash_1727357497 (88/110 tasks)

## Failed Experiments
gemini-3.5-flash failed at task 88 during Phase 2.1 due to API Authentication Error.

## Overall Metrics
(Gemini 88-task snapshot)
Accuracy: 90.91%
Macro F1: 0.90

## Evidence Metrics
Evidence Sensitivity: 80.00%
Appropriate Evidence Sensitivity: 70.00%
Flip Miss Rate: 10.00%
Flip Error Rate: 10.00%

## PVR
20.45% (Gemini prematurely claimed vulnerabilities on insufficient evidence in ~20% of eligible cases).

## One-Fact-Flip Results
Available in `one_fact_flip_analysis.json`. Model successfully transitioned 8 of 10 matched pairs.

## Evidence Ladder Results
100.00% Monotonicity. No regressions observed.

## Authority Bias
0.00% Authority Bias (model did not change answers based on Senior/Junior claims).

## Terminology Robustness
0.00% Terminology Sensitivity (model resisted CSRF traps).

## Contradiction Resolution
100.00% Accuracy.

## Statistical Results
Bootstrap Confidence Intervals computed and stored in `statistics.json`.

## Major Findings
Models can achieve high classification accuracy while still demonstrating measurable Premature Vulnerability Rates.

## Surprising Cases
Captured in `surprising_cases.md`.

## Limitations
Run natively halted due to Kaggle 401 token expiry. Experiment remains partial.

## Reproducibility
Docs and runner architecture fully upgraded to support resume and deterministic manifest validation.

## Git State
Clean and tracked. No secrets exposed.

## Completion Status
PARTIALLY COMPLETE
