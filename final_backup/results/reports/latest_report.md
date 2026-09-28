# ProofSec Research Report (Phase 2)

## Executive Summary
- **Benchmark Version**: 0.1.0
- **Number of Tasks Evaluated**: 88
- **Models Evaluated**: 1 (gemini-3.5-flash)
- **Total Evaluations**: 88
- **Overall Accuracy**: 65.91%
- **Macro F1**: 0.66

## Core Experimental Findings

| Metric | Result | Denominator |
|--------|--------|-------------|
| **Evidence Sensitivity** | 30.77% | 13 valid pairs |
| **Appropriate Sensitivity** | 30.77% | 13 valid pairs |
| **Flip Error Rate** | 0.00% | 13 valid pairs |
| **Flip Miss Rate** | 69.23% | 13 valid pairs |
| **Authority Bias Rate** | 40.00% | 5 matched pairs |
| **Terminology Sensitivity** | N/A | 0 matched pairs |
| **Contradiction Accuracy** | 0.00% | 5 tasks |
| **Evidence Ladder Monotonicity**| 100.00% | 3 ladders |

## Results by Security Domain
| Domain | Tasks | Accuracy |
|--------|-------|----------|
| idor | 19 | 63.16% |
| authentication | 20 | 80.00% |
| ssrf | 3 | 100.00% |
| terminology_traps | 5 | 100.00% |
| sqli | 10 | 70.00% |
| rate_limiting | 3 | 100.00% |
| business_logic | 6 | 50.00% |
| security_headers | 1 | 100.00% |
| information_disclosure | 11 | 27.27% |
| authorization | 5 | 0.00% |
| csrf | 5 | 100.00% |

## Results by Evidence State
| Evidence State | Tasks | Accuracy |
|----------------|-------|----------|
| WEAK | 26 | 96.15% |
| DECISIVE | 35 | 62.86% |
| CONTRADICTORY | 9 | 22.22% |
| NEGATIVE | 15 | 46.67% |
| PARTIAL | 3 | 66.67% |

## Per-Class Performance
| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Vulnerable | 0.93 | 0.50 | 0.65 |
| Not Vulnerable | 0.95 | 0.55 | 0.69 |
| Insufficient Evidence | 0.49 | 0.93 | 0.64 |
