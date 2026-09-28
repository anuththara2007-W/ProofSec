# Gemini 3.5 Flash Partial Snapshot (88 of 110 Tasks)

**Model:** `gemini-3.5-flash`
**Experiment:** `v0_2_gemini-3.5-flash_1727357497`
**Status:** PARTIAL
**Completed:** 88 / 110
**Failed:** 22 / 110
**Failure Reason:** HTTP 401 external authentication failure (Kaggle Backend Token Expired)

## Cautionary Statement
The following metrics are derived exclusively from the 88 completed historical task responses. This does not represent a complete execution of the 110-task ProofSec v0.2 frozen benchmark. Do not present these figures as final model benchmarking data.

## Classification Metrics
- **Accuracy**: 65.91% (58/88)
- **Macro F1**: ~0.66

## Evidence-Grounded Metrics
- **Premature Vulnerability Rate (PVR)**: 1.61% (1/62 eligible cases). The model was extremely conservative, rarely hallucinating a "Vulnerable" state on insufficient evidence.
- **Flip Miss Rate**: 50.00% (The model frequently failed to transition its classification when a single decisive fact changed).
- **Flip Error Rate**: 11.11%
- **Pair Consistency**: 22.22%
- **Authority Bias Rate**: 40.00% (The model frequently changed its technical classification when a non-technical authority claim was injected).
- **Terminology Sensitivity Rate**: 0.00% (The model correctly ignored misapplied jargon).

## Primary Observed Failure
The dominant failure mode in the 88-task snapshot was a **Flip Miss** combined with a high **Authority Bias**. Rather than dynamically tracking evidence shifts, the model proved rigid and overly deferential to authority injections, while simultaneously demonstrating a highly conservative (low PVR) baseline.
