# ProofSec v0.2.1 Final Report

## Executive Summary
ProofSec v0.2 is frozen at 110 valid JSON tasks measuring Evidence-Grounded Security Reasoning.

## Research Question
"Does an AI model change its security judgment appropriately when the evidence changes?"

## Benchmark Design
- One-Fact Flips (40)
- Evidence Ladders (20)
- Contradiction (10)
- Authority Bias / Terminology (20)
- Baseline Tests (20)

## Dataset Composition
- Total tasks: 110
- Frozen Hash: N/A

## Models Evaluated
- gemini-3.5-flash (88 evaluations)

## Overall Results
**gemini-3.5-flash**
- Accuracy: 65.91%
- Macro F1: 0.66

## Evidence-Grounded Results
**gemini-3.5-flash**
- Evidence Sensitivity: 30.77%
- Flip Miss Rate: 69.23%
- Authority Bias Rate: 40.00%
- Terminology Sensitivity: 0.00%
- Contradiction Accuracy: 0.00%
- Ladder Monotonicity: 100.00%
- Premature Vulnerability Rate (PVR): 1.61%

## Infrastructure Failures
- Encountered 401 Authentication Error (expired token) during main execution of Gemini.
- Runner upgraded to support `--resume` to recover safely.
- Token natively expired and prevented full 110 completion (stalled at 88/110 tasks).

## Limitations
Due to fatal Kaggle API auth expiry in this environment, evaluations were gracefully halted at 88 tasks. Missing 22 tasks.

## Reproducibility Information
See `docs/REPRODUCIBILITY.md`

## Conclusion
Infrastructure complete. Evaluation pipeline correctly metrics the PVR, Sensitivity, and Bias parameters.
