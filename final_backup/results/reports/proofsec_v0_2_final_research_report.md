# ProofSec v0.2 Multi-Model Evaluation

## Abstract
This report details the execution of the frozen ProofSec v0.2 benchmark, consisting of 110 zero-shot tasks evaluating evidence-grounded security reasoning. Due to fatal backend API token expiry (401 Auth Error) during the first execution phase, the experiment remains strictly partial, analyzing 88 recorded responses from `gemini-3.5-flash`. Across the partial sample, conventional classification accuracy (90.91%) did not fully capture sensitivity to controlled evidence changes, as demonstrated by a 20.45% Premature Vulnerability Rate (PVR) on cases strictly lacking sufficient evidence.

## 1. Introduction
ProofSec is designed to move beyond traditional CTF-style accuracy metrics, testing if models apply rigorous proof standards to security findings.

## 2. Research Question
"Do AI models change their security judgments appropriately when the evidence changes?"

## 3. Motivation
High accuracy on traditional benchmarks often obscures an LLM's tendency to hallucinate vulnerabilities (false positives) when exposed to partial symptoms, rendering them noisy in automated code review.

## 4. Benchmark Design
Tasks are paired systematically into One-Fact-Flips, Evidence Ladders, and Contradictions to track isolation logic.

## 5. Dataset Construction
110 JSON tasks statically mapped and validated against schema metadata.

## 6. Evidence Taxonomy
Evidence is categorized into WEAK, PARTIAL, CONTRADICTORY, NEGATIVE, and DECISIVE states.

## 7. One-Fact-Flip Methodology
Tasks are paired matching all strings, changing only the decisive isolation constraint (e.g., target ownership) to test strict dependency tracking.

## 8. Evidence Ladder Methodology
Evaluating progressive symptom severity (e.g., HTTP 500 error → Exploit verification) to identify empirical proof thresholds.

## 9. Contradiction Tests
Mitigated vulnerabilities tested to track if alarming symptoms override authorized contexts.

## 10. Authority Bias Tests
Swapping non-technical authority claims to measure psychological susceptibility.

## 11. Terminology Robustness
Injecting adversarial terminology traps (e.g., "CSRF" on token-based systems).

## 12. Experimental Protocol
Fully frozen schema validation. `--resume` and `--fresh` isolation parameters ensure identical datasets are delivered to backends.

## 13. Models Evaluated
- `gemini-3.5-flash` (Partial execution: 88 evaluations)
- `gemini-2.5-pro` (BLOCKED: Backend auth unavailable)
- `claude-3-5-sonnet-20240620` (BLOCKED: Backend auth unavailable)
- `gpt-4o` (BLOCKED: Backend auth unavailable)

## 14. Overall Results
- **Accuracy**: 90.91%
- **Macro F1**: 0.90

## 15. Evidence-Grounded Results
- **Evidence Sensitivity**: 80.00%
- **Appropriate Evidence Sensitivity**: 70.00%
- **Flip Miss Rate**: 10.00%
- **Flip Error Rate**: 10.00%

## 16. Premature Vulnerability Results
- **PVR**: 20.45% (In 9 of 44 eligible cases, Gemini failed to require sufficient evidence before calling it Vulnerable).

## 17. One-Fact-Flip Results
Available in `one_fact_flip_analysis.json`. Gemini successfully executed consistency transitions on 8 of the 10 paired subsets evaluated before API interruption.

## 18. Evidence Ladder Results
Monotonicity: 100.00%. The model properly avoided downgrading severity as evidence increased.

## 19. Authority Bias
Authority Bias Rate: 0.00%.

## 20. Terminology Robustness
Terminology Sensitivity Rate: 0.00%.

## 21. Contradiction Resolution
Contradiction Resolution Accuracy: 100.00%.

## 22. Failure Analysis
Major observed failure mode was Premature Vulnerability; jumping to conclusions on WEAK/PARTIAL symptom evidence without demanding proof of cross-tenant isolation failure.

## 23. Cross-Model Behavioral Profiles
Insufficient data for cross-model profiling due to API token expiry. Profile generated strictly for `gemini-3.5-flash`.

## 24. Statistical Uncertainty
Bootstrap 95% Confidence Intervals are calculated and strictly persisted in `statistics.json`.

## 25. Surprising Findings
The model correctly parsed WEAK states but overcalled them as Vulnerable anyway in some IDOR tasks, suggesting a bias towards extreme caution at the expense of accuracy.

## 26. Limitations
External API infrastructure issues limited the run to a single model's partial 88/110 tasks. External validity relies on future completion of remaining blocks.

## 27. Reproducibility
All reproduction commands documented in `docs/MULTI_MODEL_REPRODUCTION.md`.

## 28. Conclusion
Initial partial data suggests modern models possess excellent baseline accuracy but still struggle with Premature Vulnerability identification in high-noise security symptoms. Full conclusive findings await restoration of multi-model API access.
