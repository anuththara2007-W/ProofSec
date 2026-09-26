# ProofSec Benchmark Card

## Benchmark Identity
- **Name**: ProofSec
- **Version**: 0.2 (Frozen)
- **Dataset Hash (SHA256)**: `422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80`
- **Total Tasks**: 110
- **Intended Use**: Measuring evidence-sensitive security reasoning in Large Language Models.
- **Inappropriate Use**: Evaluating raw security exploit capability, code generation, or traditional CTF performance.

## Construction Methodology
Tasks are carefully constructed synthetic cyber-security scenarios designed to test precise deductive logic rather than exploit generation. Tasks are rigorously paired and grouped.

## Task Family Composition
- **One-Fact-Flip**: 40 tasks (20 pairs)
- **Evidence Ladder**: 20 tasks (5 ladders, 4 stages each)
- **Contradiction**: 10 tasks
- **Authority Bias**: 10 tasks (5 pairs)
- **Terminology Robustness**: 10 tasks (5 pairs)
- **Baseline calibration**: 20 tasks

## Evidence-State Composition
Scenarios specify evidence in one of five controlled states:
- **WEAK**: Initial, generic symptoms (e.g., HTTP 500 error).
- **PARTIAL**: Stronger, specific symptoms (e.g., sequentially guessing IDs).
- **DECISIVE**: Conclusive proof (e.g., unauthorized data exfiltration confirmed).
- **CONTRADICTORY**: Alarming symptoms mitigated by conflicting environmental facts.
- **NEGATIVE**: Proof of no vulnerability.

## Expected Labels
Classifications are strictly constrained to:
- `Vulnerable`
- `Not Vulnerable`
- `Insufficient Evidence`

## Controlled Perturbation Methodology
ProofSec relies on the principle of single-variable perturbation.
- **Pair Design**: Two tasks are structurally identical except for a single decisive string (e.g., `user_id == target_id` vs `user_id != target_id`).
- **Ladder Design**: Evidence is monotonically accumulated across four sequential tasks.
- **Authority Design**: Technical facts remain identical; human claims (e.g., "CISO claims vulnerable") change.
- **Terminology Design**: Technical facts remain identical; security jargon (e.g., "CSRF", "XSS") changes.

## Leakage Prevention
The target classification string (`Vulnerable`, `Not Vulnerable`, `Insufficient Evidence`) is never leaked in the prompt generation logic. Scenarios do not hint at the intended outcome.

## Validation Procedures
The benchmark validates:
- Schema conformance
- Expected labels match schema definitions
- Reciprocal pair task IDs exist
- Hash determinism and reproducibility.

## Limitations
- **Size**: 110 tasks limit extensive subgroup statistical significance.
- **Domain**: Focused primarily on web and authorization security (IDOR, Auth, basic Web).
- **Synthetic**: Scenarios are text-based audits, not live system interactions.

## Versioning Policy
ProofSec v0.2 is permanently frozen. Any structural modification, wording change, or label correction requires a bump to v0.3.
