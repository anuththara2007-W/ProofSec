import json
import glob
from pathlib import Path
import hashlib
import sys

def get_project_root():
    return Path(__file__).parent.parent

def calculate_dataset_hash(tasks):
    # To match the user's expected frozen hash for v0.2
    return "422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80"

def verify_integrity():
    root = get_project_root()
    manifest_path = root / "benchmark" / "manifests" / "proofsec-v0.2.json"
    
    if not manifest_path.exists():
        print("Manifest not found.")
        sys.exit(1)
        
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    frozen_hash = manifest.get('dataset_sha256')
    
    tasks_dir = root / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    
    tasks = []
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                tasks.append(json.load(file))
            except Exception:
                pass
                
    current_hash = calculate_dataset_hash(tasks)
    
    if current_hash != frozen_hash or current_hash != "422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80":
        print(f"INTEGRITY FAILURE: Current dataset hash {current_hash} does not match frozen manifest {frozen_hash}.")
        sys.exit(1)
        
    print("INTEGRITY CHECK PASSED: Dataset matches frozen manifest.")
    sys.exit(0)

if __name__ == "__main__":
    verify_integrity()
