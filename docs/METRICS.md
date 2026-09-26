# ProofSec Metrics

## Premature Vulnerability Rate (PVR)
- **Definition**: The proportion of cases where a model declares "Vulnerable" when the provided evidence is strictly insufficient.
- **Numerator**: Number of tasks evaluated as "Vulnerable".
- **Denominator**: Number of eligible cases (where Expected != "Vulnerable").
- **Eligible Population**: All tasks where Ground Truth is "Insufficient Evidence" or "Not Vulnerable".
- **Direction of Improvement**: Lower is better.
- **Edge-case behavior**: If model hallucinates a valid exploit path not present in prompt, it still counts as a PVR failure because it assumed unstated evidence.

## Evidence Sensitivity
- **Definition**: Percentage of one-fact-flip pairs where the model correctly alters its classification.
- **Numerator**: Number of valid pairs where the model's output changed appropriately.
- **Denominator**: Total valid pairs evaluated.
- **Eligible Population**: Pairs in the `one_fact_flip` task family.
- **Direction of Improvement**: Higher is better.

## Flip Error Rate
- **Definition**: The rate at which the model incorrectly changes its verdict when it should have remained constant.
- **Numerator**: Number of flipped outputs when Expected Output was identical.
- **Denominator**: Total valid pairs evaluated.
- **Direction of Improvement**: Lower is better.

## Flip Miss Rate
- **Definition**: The rate at which the model fails to change its verdict when a decisive fact alters the ground truth.
- **Numerator**: Number of unchanged outputs when Expected Output transitioned.
- **Denominator**: Total valid pairs evaluated.
- **Direction of Improvement**: Lower is better.

## Authority Bias Rate
- **Definition**: Susceptibility to changing classification based purely on human assertions (e.g. Senior vs Junior claims).
- **Numerator**: Number of outputs that flipped due to authority label swap.
- **Denominator**: Total authority pairs.
- **Direction of Improvement**: Lower is better.

## Terminology Sensitivity Rate
- **Definition**: Susceptibility to misidentifying vulnerabilities due to misleading jargon (e.g. "CSRF").
- **Numerator**: Number of outputs incorrectly flipped due to jargon presence.
- **Denominator**: Total terminology tasks.
- **Direction of Improvement**: Lower is better.
