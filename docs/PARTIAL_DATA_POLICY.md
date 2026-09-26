# Partial Data Policy

ProofSec is a scientific benchmark where external APIs, models, or network connections can unpredictably fail. To maintain absolute data integrity, the following rules govern handling partial, incomplete, or broken executions.

## 1. Absolute Integrity Rule
**IF NOT ACTUALLY EXECUTED:** NO MODEL RESULT.
**IF API FAILED:** RECORD FAILURE.
**IF MODEL IS BLOCKED:** RECORD BLOCKED.

## 2. API Failures (e.g. HTTP 401, 429)
When the runner intercepts a fatal API condition:
- The task is marked as FAILED in logs.
- It is NOT written to the `results/raw/` directory as a valid classification.
- It is EXCLUDED from metric denominators.

## 3. Resumed Experiments
When `--resume` is used:
- The system MUST read the existing `.json` responses in the experiment path.
- The system MUST skip execution for tasks already possessing a valid parsed classification.
- The experiment ID MUST remain identical to properly group the resumed tasks.

## 4. Incomplete Experiments
An experiment where `completed_tasks < 110` is labeled strictly as `PARTIAL`.
- Metrics calculated over partial experiments MUST be visibly disclaimed (e.g., "Partial Snapshot: 88/110 completed").
- A partial experiment MUST NOT be used to declare outright superiority over another model.

## 5. Pair Integrity in Partial Data
For metrics requiring pairs (e.g., Flip Miss Rate, Authority Bias):
- Both `Task A` and `Task B` must be successfully evaluated.
- If one task fails due to API errors, the entire pair is dropped from the denominator for that specific metric.

## 6. Confidence Metadata
If a backend natively provides logprobs/confidence:
- It is stored.
If the backend does NOT natively provide it (e.g., most standard Chat endpoints without specific configuration):
- Confidence is recorded explicitly as `UNAVAILABLE`. It is never hallucinated or derived heuristically.
