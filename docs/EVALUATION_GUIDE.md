# ProofSec Evaluation Guide

## Introduction
The ProofSec platform is fundamentally designed to evaluate Large Language Models (LLMs) on their ability to perform strict, evidence-grounded security reasoning. It opposes the tendency of models to hallucinate vulnerabilities based on weak indicators, buzzwords, or adversarial prompting.

## Conducting a Custom Evaluation

1. **Start the API Server**
   ```bash
   proofsec serve --port 8000
   ```
2. **Open the Dashboard**
   Navigate to `http://localhost:8000`.
3. **Submit a Scenario**
   Provide a scenario description, context, and the initial pieces of observed evidence.
4. **Iterative Revision**
   Do not modify original evaluations. Instead, use the **Revise** feature in the dashboard (or via `/api/v1/evaluations/{id}/revise`) to append new evidence. ProofSec tracks the evaluation timeline securely.

## Optional Ground Truth
When conducting custom evaluations (not the frozen benchmark), you may supply optional ground truth (`expected_classification`, `expected_evidence_state`, `expected_decisive_fact`).
- The ground truth is strictly withheld from the model prompt.
- The API calculates a comparison matrix, outputting `metrics` on accuracy and classification correctness.

## Differentiating Reports
ProofSec strictly separates terminology to preserve scientific honesty:
- **Designed Benchmark**: The set of theoretical tasks defined in the codebase.
- **Executed Benchmark**: A full 100% run of a benchmark.
- **Partial Experiment**: When an execution fails to complete (e.g., provider timeouts, 401 Unauthorized), the system logs a partial experiment. Do not treat this as an "Executed Benchmark".

## Reproducibility
Every custom evaluation and official benchmark experiment is assigned a deterministic UUID or timestamp ID. Use `proofsec research replay <id>` to verify available data and run offline analytics.
