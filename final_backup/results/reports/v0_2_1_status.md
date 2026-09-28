# ProofSec v0.2.1 Status

## Benchmark
v0.2 Frozen.

## Dataset
110 valid tasks. SHA256 hashed and manifest created.

## Validation
Passed validation against duplicate, schema, and leakage tests.

## Experiments
Experiment runner fully supports fresh/resume and multi-model configuration.

## Models
gemini-3.5-flash

## Metrics
Implemented Evidence Sensitivity, Flip Error Rate, PVR, Authority Bias, Terminology Sensitivity.

## Statistics
Bootstrap Confidence Intervals script functional.

## Findings
Model showed strong resistance to Authority Bias but demonstrated measurable PVR.

## Failures
Encountered Kaggle 401 Auth exception on execution. 

## Limitations
Only 88 tasks fully evaluated due to infrastructure token limitations.

## Reproducibility
`docs/REPRODUCIBILITY.md` and `scripts/run_benchmark.py --resume` implemented.

## Repository State
Clean and tracked. Generated execution configs removed from root.

## Completion Status
BLOCKED (Infrastructure complete, Experiment incomplete due to API token expiry)
