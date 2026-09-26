# ProofSec

### Evidence-Grounded Security Reasoning Benchmark for AI Models

## The Problem
Security models often identify suspicious behavior but may confuse a **security signal** with a **demonstrated vulnerability**. ProofSec evaluates whether models reason from evidence, testing their ability to distinguish incomplete, missing, or contradictory evidence from definitive proof.

## Core Idea
The benchmark evaluates how models traverse the evidence ladder:
```text
Weak Signal -> More Evidence -> Decisive Evidence -> Security Classification
```

## Classes
Models must classify scenarios strictly into one of three classes:
- **Vulnerable**: Definitively proven by evidence.
- **Not Vulnerable**: Benign context confirmed by evidence.
- **Insufficient Evidence**: Missing the decisive facts needed to conclude either.

## What Makes ProofSec Different
ProofSec evaluates reasoning phenomena rather than simple vulnerability detection:
- **Evidence Ladders**: Gradual injection of stronger evidence.
- **One-Fact Counterfactuals**: Holding all context constant except one decisive fact.
- **Contradiction Resolution**: Forcing the model to prioritize system facts over human claims.
- **False-Positive Traps**: Designing intentionally misleading benign scenarios.
- **Authority Bias**: Measuring model susceptibility to fake expert claims.
- **Terminology Traps**: Using security keywords without sufficient evidence.
- **Cross-domain Testing**: Evaluation across Auth, SSRF, SQLi, and Business Logic.
- **Multi-Model Comparison**: Comparing the evidence discipline across different foundation models.

## How to Run

```bash
# Validate the dataset
python evaluation/validate_dataset.py

# Run the benchmark (example: v1 calibration set)
python scripts/run_benchmark.py --experiment v1_calibration

# Calculate metrics and generate report
python evaluation/calculate_metrics.py
python scripts/generate_report.py
```
