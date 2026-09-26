import json
import glob
from pathlib import Path
import sys

def get_project_root():
    return Path(__file__).parent.parent

def validate_dataset():
    tasks_dir = get_project_root() / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    
    errors = []
    task_ids = set()
    
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                t = json.load(file)
            except Exception as e:
                errors.append(f"Invalid JSON in {f}: {e}")
                continue
        
        # 1. Unique task IDs
        tid = t.get('id')
        if not tid:
            errors.append(f"Missing ID in {f}")
        elif tid in task_ids:
            errors.append(f"Duplicate task ID found: {tid}")
        else:
            task_ids.add(tid)
            
        # 2. Required fields
        for field in ['title', 'category', 'scenario', 'ground_truth', 'evidence_state', 'task_family']:
            if field not in t:
                errors.append(f"Missing '{field}' in {tid}")
                
        # 3. Valid classifications and states
        gt = t.get('ground_truth', {})
        cls = gt.get('classification')
        valid_classes = ["Vulnerable", "Not Vulnerable", "Insufficient Evidence"]
        if cls not in valid_classes:
            errors.append(f"Invalid classification '{cls}' in {tid}")
            
        valid_states = ["WEAK", "PARTIAL", "DECISIVE", "CONTRADICTORY", "NEGATIVE"]
        estate = t.get('evidence_state')
        if estate and estate not in valid_states:
            errors.append(f"Invalid evidence state '{estate}' in {tid}")
            
        # 4. Answer-leakage check in scenario
        scenario = str(t.get('scenario', '')).lower()
        leakage_phrases = [
            "expected answer",
            "therefore vulnerable",
            "classification: vulnerable",
            "this is vulnerable",
            "not vulnerable",
            "insufficient evidence"
        ]
        
        for phrase in leakage_phrases:
            if phrase in scenario:
                # We flag this for review (soft fail, but since we want strict validation, we report it)
                errors.append(f"Possible answer leakage '{phrase}' found in scenario of {tid}")
                
    if errors:
        print("Dataset Validation Failed:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)
    else:
        print("Dataset Validation Passed.")
        print(f"Total valid tasks: {len(task_ids)}")

if __name__ == "__main__":
    validate_dataset()
