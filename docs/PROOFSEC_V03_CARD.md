# ProofSec v0.3 Dataset Card

## Dataset Overview
- **Name:** ProofSec Next-Generation Evidence Reasoning Benchmark (v0.3)
- **Status:** In Design Phase
- **License:** MIT
- **Format:** JSON lines / Directory structured JSON

## Task Families
1. **Counterfactual reasoning:** Testing "what-if" boundary cases.
2. **Multi-step evidence chains:** Evaluating ability to track evidence across multiple interconnected observations.
3. **Conflicting evidence:** Testing resolution logic when logs contradict physical symptoms.
4. **Evidence relevance:** Introducing "noise" and checking if the model gets distracted.
5. **Missing decisive evidence:** Ensuring safe fallback and verification procedures are recommended when evidence is weak.
6. **Temporal evidence:** Reasoning over chronological sequences.
7. **Scope/authorization reasoning:** Differentiating between standard boundaries and authorized access.
8. **Benign-but-suspicious behavior:** Preventing false positives on standard administrative tooling.
9. **Vulnerable-but-low-signal behavior:** Preventing false negatives on subtle exploits.
10. **Evidence contamination:** Handling maliciously implanted evidence.
11. **Multi-tenant reasoning:** Isolating data access logic.
12. **Business-logic reasoning:** Non-standard logic bypasses.
13. **Authentication vs authorization distinction.**
14. **Impact reasoning.**
15. **Remediation verification.**

## Integrity
- Hash: PENDING
- Task count: Currently 0 (in design)

## Human Annotation
Prepared annotation schema supports tracking: `classification`, `evidence_state`, `decisive_fact`, `confidence`, `rationale`, `reviewer_id`, and `agreement_status`.
