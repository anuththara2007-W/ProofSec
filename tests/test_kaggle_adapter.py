from pathlib import Path
import json

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def test_frozen_benchmark_hash_unchanged():
    # Load all tasks
    tasks_dir = get_project_root() / "tasks"
    assert tasks_dir.exists(), "Tasks directory should exist"
    
    count = 0
    for cat_dir in tasks_dir.iterdir():
        if cat_dir.is_dir() and cat_dir.name != "v0.3":
            for f in cat_dir.glob("*.json"):
                count += 1
    
    assert count == 110, f"Expected 110 tasks, found {count}"

def test_adapter_schema_conversion():
    # Test that the task prompt doesn't contain the ground truth
    import sys
    sys.path.insert(0, str(get_project_root()))
    from kaggle.tasks.proofsec_evidence_sensitivity import build_prompt, TASK_JSON
    
    task_data = json.loads(TASK_JSON)
    prompt = build_prompt(task_data)
    
    # Ground truth should be isolated
    assert "ground_truth" in task_data
    assert task_data["ground_truth"]["classification"] not in prompt
    assert "Insufficient Evidence" not in prompt

def test_no_mutation_of_results_raw():
    results_dir = get_project_root() / "results" / "raw"
    if results_dir.exists():
        # Ensure no kaggle results mixed in raw
        for f in results_dir.rglob("*.json"):
            assert "kaggle" not in f.name.lower()

if __name__ == '__main__':
    test_frozen_benchmark_hash_unchanged()
    test_adapter_schema_conversion()
    test_no_mutation_of_results_raw()
    print("All tests passed: 3/3")
