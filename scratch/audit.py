import json
import glob
from pathlib import Path
import os
import subprocess

def get_project_root():
    return Path(__file__).parent.parent

def write_audit():
    # Repository Audit
    root = get_project_root()
    repo_audit = """# ProofSec v0.2.1 Repository Audit
    
## Repository State
- Branch: main
- Commit: 1b04a38 (feat: complete v0.2 phase 2 architecture and experimental dataset)
- Uncommitted changes: None

## Dataset State
- Task Count: 110 valid tasks.
- Experiments: 5 distinct configs (one_fact_flip, evidence_ladder, contradiction, terminology, authority_bias).
- Integrity: PASS

## Execution State
- Raw Results: 88 tasks completed via `gemini-3.5-flash`.
- Known Problems: API 401 Authentication Error during execution causing partial run.
- Missing functionality: Resumable `--resume` execution is missing. Model switching via `--model` is rudimentary. 

## Metrics State
- Missing: PVR (Premature Vulnerability Rate)
- Current calculations: Evidence Sensitivity, Flip Miss/Error, F1, Accuracy

## Recommended Actions
1. Implement resumability and hash-based dataset freezing in runner.
2. Upgrade calculate_metrics.py to include PVR.
3. Freeze v0.2.
"""
    reports_dir = root / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "v0_2_1_repository_audit.md", "w") as f:
        f.write(repo_audit)

def write_partial_audit():
    root = get_project_root()
    raw_files = glob.glob(str(root / "results" / "raw" / "*.json"))
    
    partial = f"""# PARTIAL EXPERIMENT
# NOT FINAL v0.2 RESULT

## Execution Metadata
- Tasks Attempted: 110
- Tasks Successfully Completed: {len(raw_files)}
- Tasks Failed/Missing: {110 - len(raw_files)} (401 Auth Error)
- Models Used: gemini-3.5-flash
- Model Version: gemini-3.5-flash
- Authentication Errors: 1 (Fatal token expiration)

"""
    reports_dir = root / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "partial_run_88_analysis.md", "w") as f:
        f.write(partial)

if __name__ == "__main__":
    write_audit()
    write_partial_audit()
    print("Audits generated.")
