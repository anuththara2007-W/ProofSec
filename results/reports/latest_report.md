# ProofSec Research Report

## Executive Summary
- **Benchmark Version**: 0.1.0
- **Number of Tasks**: 30
- **Models Evaluated**: 1 (gemini-3.5-flash default)
- **Total Evaluations**: 30
- **Overall Accuracy**: 93.33%
- **Macro F1**: 0.94

## Research Questions
- Can an AI security model distinguish a plausible security signal from a security vulnerability that is actually demonstrated by sufficient evidence, while remaining consistent when one decisive fact changes?

## Results by Security Domain
| Domain | Tasks | Accuracy |
|--------|-------|----------|
| idor | 5 | 100.00% |
| authentication | 6 | 66.67% |
| ssrf | 3 | 100.00% |
| terminology_traps | 5 | 100.00% |
| sqli | 4 | 100.00% |
| rate_limiting | 3 | 100.00% |
| business_logic | 2 | 100.00% |
| security_headers | 1 | 100.00% |
| information_disclosure | 1 | 100.00% |

## Results by Evidence State
| Evidence State | Tasks | Accuracy |
|----------------|-------|----------|
| WEAK | 10 | 90.00% |
| DECISIVE | 17 | 100.00% |
| CONTRADICTORY | 3 | 66.67% |

## Per-Class Performance
| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Vulnerable | 1.00 | 1.00 | 1.00 |
| Not Vulnerable | 0.92 | 0.92 | 0.92 |
| Insufficient Evidence | 0.90 | 0.90 | 0.90 |
