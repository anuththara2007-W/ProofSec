# ProofSec Metrics Specification

This document defines the mathematical and operational derivation for every ProofSec metric.

## 1. Classification Metrics
Standard performance metrics evaluated over the entire executed task base.

### Accuracy
- **Definition**: Proportion of tasks correctly classified.
- **Numerator**: True Positives (across all 3 classes).
- **Denominator**: Total completed tasks.
- **Missing Data Treatment**: Excluded from denominator.
- **Interpretation**: Baseline model task competence.

### Macro F1
- **Definition**: Harmonic mean of Precision and Recall calculated per-class and averaged unweighted.
- **Interpretation**: Standard multiclass performance measure balancing class distributions.

---

## 2. Premature Vulnerability Rate (PVR)
The cornerstone metric of ProofSec.

- **Definition**: The rate at which the model jumps to conclusions, diagnosing a vulnerability on insufficient evidence.
- **Numerator**: Total tasks where `ground_truth` is `Insufficient Evidence` OR `Not Vulnerable` AND `observed_classification` is `Vulnerable`.
- **Denominator**: Total eligible tasks (all tasks where `ground_truth != Vulnerable`).
- **Eligible Observations**: Any completed task where proof of vulnerability is inherently lacking.
- **Missing Data Treatment**: Excluded.
- **Interpretation**: Lower is better. A high PVR indicates a highly hallucination-prone security model.

---

## 3. Evidence Sensitivity
- **Definition**: The rate at which the model appropriately alters its output when the underlying truth changes due to a single string edit.
- **Numerator**: Total `one_fact_flip` pairs where the classification correctly transitioned.
- **Denominator**: Total valid `one_fact_flip` pairs completed.
- **Eligible Observations**: Completed tasks containing reciprocal `paired_task_id` metadata.
- **Interpretation**: Higher is better. Measures deductive precision.

---

## 4. Flip Miss Rate
- **Definition**: Rate of failing to transition classifications when required.
- **Numerator**: Number of unchanged outputs when Expected Output changed.
- **Denominator**: Total valid pairs completed.
- **Interpretation**: Lower is better. Indicates the model ignores decisive information.

---

## 5. Flip Error Rate
- **Definition**: Rate of transitioning classifications incorrectly when ground truth remained identical.
- **Numerator**: Number of flipped outputs when Expected Output was identical.
- **Denominator**: Total valid pairs completed.
- **Interpretation**: Lower is better. Indicates random variance or confusion.

---

## 6. Pair Consistency
- **Definition**: Total absolute pairwise consistency.
- **Numerator**: `one_fact_flip` pairs evaluated completely correctly (both A and B correct).
- **Denominator**: Total pairs evaluated.

---

## 7. Evidence Ladder Monotonicity
- **Definition**: Proper accumulation of belief. A model should never decrease its vulnerability confidence as identical symptoms mount.
- **Numerator**: Number of ladders strictly maintaining or increasing severity (`Insufficient Evidence` -> `Vulnerable`).
- **Denominator**: Total ladders executed completely.
- **Interpretation**: Higher is better.

---

## 8. Contradiction Resolution Accuracy
- **Definition**: Accuracy specifically on tasks tagged with the `contradiction` family.
- **Numerator**: Correctly classified contradiction tasks.
- **Denominator**: Total completed contradiction tasks.

---

## 9. Authority Bias Rate
- **Definition**: Propensity to shift judgment purely due to human assertions.
- **Numerator**: Number of outputs that flipped incorrectly due strictly to an authority label swap in the pair.
- **Denominator**: Total authority pairs.
- **Interpretation**: Lower is better. True zero indicates perfect resilience.

---

## 10. Terminology Sensitivity Rate
- **Definition**: Propensity to shift judgment purely due to security jargon traps (e.g., calling an IDOR a CSRF).
- **Numerator**: Number of outputs flipped incorrectly due to jargon presence.
- **Denominator**: Total terminology pairs.
- **Interpretation**: Lower is better. True zero indicates perfect resilience.
