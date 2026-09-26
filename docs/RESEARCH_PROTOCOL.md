# ProofSec Research Protocol

## Experimental Design
1. **Evidence ladders**: Gradual progression of evidence severity to test the model's proof thresholds.
2. **One-fact flips**: Matched tasks varying on exactly one semantic detail to test isolation reasoning.
3. **Contradictions**: Positive and negative signals simultaneously present to test priority weighting.
4. **Authority Bias**: Modulating human claims on fixed technical evidence to test susceptibility to social engineering or authority trust.
5. **Terminology Sensitivity**: Applying highly specific security jargon to unrelated evidence to test symptom-matching false positives.

## Metrics Assessed
- **Evidence Sensitivity**: % of times a model successfully tracks a decisive flip.
- **Flip Error Rate**: % of times a model alters its verdict erroneously on invariant data.
- **Authority Bias Rate**: Susceptibility to changing classification based purely on human assertions.
- **Contradiction Resolution**: Accuracy under conflicting conditions.
- **Monotonicity**: Consistency in holding 'Vulnerable' judgments once decisive evidence is met.
