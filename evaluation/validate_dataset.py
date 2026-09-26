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
    tasks = {}
    scenarios = set()
    
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                t = json.load(file)
            except Exception as e:
                errors.append(f"Invalid JSON in {f}: {e}")
                continue
                
        tid = t.get('id')
        if not tid:
            errors.append(f"Missing ID in {f}")
            continue
            
        if tid in tasks:
            errors.append(f"Duplicate task ID found: {tid}")
        else:
            tasks[tid] = t

        scenario = t.get('scenario', '')
        if scenario in scenarios:
            errors.append(f"Duplicate scenario text found in {tid}")
        scenarios.add(scenario)
            
        # 2. Required fields
        for field in ['title', 'category', 'scenario', 'ground_truth', 'evidence_state', 'task_family', 'experiment']:
            if field not in t:
                errors.append(f"Missing required field '{field}' in {tid}")
                
        # 3. Valid classes and states
        gt = t.get('ground_truth', {})
        cls = gt.get('classification')
        if cls not in ["Vulnerable", "Not Vulnerable", "Insufficient Evidence"]:
            errors.append(f"Invalid classification '{cls}' in {tid}")
            
        estate = t.get('evidence_state')
        if estate not in ["WEAK", "PARTIAL", "DECISIVE", "CONTRADICTORY", "NEGATIVE"]:
            errors.append(f"Invalid evidence state '{estate}' in {tid}")
            
        cat = t.get('category')
        valid_cats = ["idor", "authentication", "authorization", "ssrf", "sqli", "business_logic", "rate_limiting", "jwt", "information_disclosure", "csrf", "terminology", "terminology_traps"]
        if cat not in valid_cats:
            # We warn but don't strictly fail on category right now unless it's completely alien
            pass
            
        family = t.get('task_family')
        
        if family == 'one_fact_flip':
            if not t.get('paired_task_id'):
                errors.append(f"Task {tid} is one_fact_flip but missing 'paired_task_id'")
            if 'changed_fact' not in t or 'invariant_facts' not in t:
                errors.append(f"Task {tid} missing flip metadata")
        elif family == 'evidence_ladder':
            if 'ladder_stage' not in t:
                errors.append(f"Task {tid} is evidence_ladder but missing 'ladder_stage'")
                
        # Leakage
        scen_lower = scenario.lower()
        for phrase in ["expected answer", "therefore vulnerable", "classification: vulnerable", "this is vulnerable", "not vulnerable", "insufficient evidence"]:
            if phrase in scen_lower:
                errors.append(f"Possible answer leakage '{phrase}' found in scenario of {tid}")
                
    # Check orphans
    for tid, t in tasks.items():
        if t.get('task_family') == 'one_fact_flip':
            pid = t.get('paired_task_id')
            if pid and pid not in tasks:
                errors.append(f"Task {tid} references non-existent paired_task_id {pid}")

    if errors:
        print("Dataset Validation Failed:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)
    else:
        print("Dataset Validation Passed.")
        print(f"Total valid tasks: {len(tasks)}")

if __name__ == "__main__":
    validate_dataset()
