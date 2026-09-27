import json
import glob
import os
import re
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def run_importer():
    root = get_project_root()
    kaggle_results_dir = root / "results" / "kaggle" / "proofsec-v0-2"
    raw_out_dir = root / "results" / "raw"
    
    # Load all frozen tasks into a dict for metadata lookup
    tasks_dir = root / "tasks"
    frozen_tasks = {}
    for f in glob.glob(str(tasks_dir / "**/*.json"), recursive=True):
        if "v0.3" in Path(f).parts:
            continue
        try:
            with open(f, 'r', encoding='utf-8') as file:
                t = json.load(file)
                frozen_tasks[t['id']] = t
        except Exception:
            continue
            
    # Find all downloaded run.json files
    run_files = glob.glob(str(kaggle_results_dir / "**/*.run.json"), recursive=True)
    print(f"Found {len(run_files)} run files.")
    
    for run_file in run_files:
        with open(run_file, 'r', encoding='utf-8') as f:
            run_data = json.load(f)
            
        model_name = run_data.get('modelVersion', {}).get('slug', 'unknown').split('/')[-1]
        model_name = model_name.replace('.', '-') # normalize naming
        
        # Create output dir for this model
        model_out_dir = raw_out_dir / f"{model_name}_kaggle"
        model_out_dir.mkdir(parents=True, exist_ok=True)
        
        assertions = run_data.get('assertions', [])
        print(f"Processing model {model_name} with {len(assertions)} assertions")
        
        for assertion in assertions:
            expectation = assertion.get('expectation', '')
            # Example: Expected: 'task-001: Insufficient Evidence', Got: 'task-001: Vulnerable'
            # Or with single quotes missing if error? No, kbench formats it with single quotes
            match = re.search(r"Expected: '([^:]+): ([^']+)', Got: '([^:]+): ([^']+)'", expectation)
            if not match:
                # Try without quotes
                match = re.search(r"Expected: ([^:]+): (.*), Got: ([^:]+): (.*)", expectation)
            
            if match:
                task_id = match.group(1)
                expected_cls = match.group(2)
                actual_cls = match.group(4)
            else:
                print(f"Failed to parse expectation: {expectation}")
                continue
                
            correct = (expected_cls == actual_cls)
            
            # Lookup metadata
            meta = frozen_tasks.get(task_id, {})
            
            result_json = {
                "benchmark_version": "0.2.0",
                "task_id": task_id,
                "model": model_name,
                "classification": actual_cls,
                "expected_classification": expected_cls,
                "correct": correct,
                "latency_ms": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0,
                "evidence_state": meta.get("evidence_state", "UNKNOWN"),
                "task_family": meta.get("task_family", "unknown"),
                "experiment": meta.get("experiment", "kaggle_evaluation"),
                "category": meta.get("category", "unknown"),
                "response": {
                    "classification": actual_cls
                }
            }
            
            out_file = model_out_dir / f"{task_id}.json"
            with open(out_file, 'w', encoding='utf-8') as out:
                json.dump(result_json, out, indent=4)
                
    print("Import complete.")

if __name__ == '__main__':
    run_importer()
