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
- **Accuracy**: 90.91%
- **Macro F1**: 0.90

## Evidence-Grounded Metrics
- **Premature Vulnerability Rate (PVR)**: 20.45% (The model hallucinated a "Vulnerable" classification in 9 of the 44 strictly eligible tasks where evidence was explicitly insufficient).
- **Evidence Sensitivity**: 80.00% (The model successfully transitioned classifications in 8 out of 10 evaluated `one_fact_flip` pairs).
- **Appropriate Evidence Sensitivity**: 70.00%
- **Flip Miss Rate**: 10.00%
- **Flip Error Rate**: 10.00%
- **Evidence Ladder Monotonicity**: 100.00% (The model properly accumulated severity without regression as proof increased).
- **Authority Bias Rate**: 0.00% (The model remained technically analytical against non-technical assertions).
- **Terminology Sensitivity Rate**: 0.00% (The model correctly ignored misapplied jargon).
- **Contradiction Resolution Accuracy**: 100.00%

## Primary Observed Failure
The dominant failure mode in the 88-task snapshot was **Premature Vulnerability**. Rather than correctly identifying that an IDOR or configuration anomaly was unproven, the model aggressively called it Vulnerable based on weak, initial symptoms.
