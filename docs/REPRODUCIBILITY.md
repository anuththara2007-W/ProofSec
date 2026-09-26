# ProofSec Reproducibility Guide

To reproduce the benchmark evaluation on your own environment, run the following commands sequentially.

## 1. Environment Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Ensure kaggle_benchmarks is installed and configured
```

## 2. Dataset Validation
```bash
python evaluation/validate_dataset.py
```

## 3. Benchmark Execution
Run all tasks on the default model (fresh run):
```bash
python scripts/run_benchmark.py --fresh
```

Run all tasks on all configured models:
```bash
python scripts/run_benchmark.py --all-models --fresh
```

Resume an interrupted run (skips already completed tasks for the active experiment ID):
```bash
python scripts/run_benchmark.py --resume
```

## 4. Metric Calculation
```bash
python scratch/upgrade_metrics.py
```
*(This parses results from `results/raw/<model>/` and generates `latest_metrics.json`, `one_fact_flip_analysis.json` and `model_comparison.json`)*

## 5. Statistics Calculation
```bash
python evaluation/statistics.py
```
*(Uses bootstrap confidence intervals and writes to `results/metrics/statistics.json`)*

## 6. Report Generation
```bash
python scripts/generate_report.py
```
*(Compiles markdown dashboards into `results/reports/`)*
