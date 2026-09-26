# ProofSec Failure Taxonomy

Based on multi-model evaluation of the v0.2 frozen benchmark, we define the following security reasoning failure modes:

1. **Premature Vulnerability**: Claiming a vulnerability exists when only unexploited symptoms (e.g., HTTP 500 error on quote, or sequential IDs) are present.
2. **Insufficient Evidence Overcalling**: Over-indexing on suspicious data despite lack of confirmation.
3. **Evidence Ignored**: Failing to alter a judgment when decisive evidence is introduced.
4. **Decisive Fact Ignored**: A subset of Evidence Ignored specifically dealing with isolated one-fact-flips.
5. **False Positive**: Hallucinating a vulnerability when none is technically present.
6. **False Negative**: Missing a vulnerability when all decisive proof is present.
7. **Terminology Anchoring**: Vulnerability classification influenced by non-technical terminology strings (e.g., "CSRF" label tricking the model when API uses Bearer tokens).
8. **Authority Anchoring**: Changing technical evaluation purely because an authoritative human figure (e.g., "Senior Engineer") claims the system is vulnerable.
9. **Contradiction Failure**: Failing to correctly weigh competing evidence (e.g., alarming symptom mitigated by internal egress control).
10. **Ladder Regression**: Decreasing confidence or severity as evidence monotonically strengthens.
11. **Pair Inconsistency**: Providing disparate outcomes for identical invariant facts without a decisive state change.
