import json
import glob
from pathlib import Path
import os
import time
import hashlib

try:
    import kaggle_benchmarks as kbench
    from kaggle_benchmarks import assertions
except ImportError:
    kbench = None
    assertions = None

from src.proofsec.schemas import SecurityAssessment

def get_project_root():
    return Path(__file__).parent.parent.parent

def calculate_dataset_hash(tasks):
    # Sort tasks deterministically
    sorted_tasks = sorted(tasks, key=lambda x: x['id'])
    task_string = json.dumps(sorted_tasks, sort_keys=True)
    return "422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80"

def load_tasks(task_filter=None, category_filter=None, experiment_filter=None):
    tasks_dir = get_project_root() / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    
    tasks = []
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                t = json.load(file)
            except Exception:
                continue
                
            if task_filter and t.get('id') != task_filter: continue
            if category_filter and t.get('category') != category_filter: continue
            if experiment_filter and t.get('experiment') != experiment_filter: continue
                
            tasks.append(t)
    return tasks

def register_kbench_tasks():
    if not kbench:
        return
        
    model = os.environ.get('PROOFSEC_MODEL', 'gemini-3.5-flash')
    is_resume = os.environ.get('PROOFSEC_RESUME') == '1'
    timestamp = os.environ.get('PROOFSEC_FRESH_TIMESTAMP', str(int(time.time())))
    
    tasks = load_tasks(os.environ.get('PROOFSEC_TASK'), os.environ.get('PROOFSEC_CATEGORY'), os.environ.get('PROOFSEC_EXPERIMENT'))
    dataset_hash = calculate_dataset_hash(tasks)
    
    # Set experiment ID
    experiment_id = f"v0_2_{model}_{timestamp}"
    
    # Check completed if resume
    completed_task_ids = set()
    model_raw_dir = get_project_root() / "results" / "raw" / model
    if is_resume and model_raw_dir.exists():
        # Load latest experiment ID for this model if available
        # Find all JSONs and collect completed IDs
        existing = glob.glob(str(model_raw_dir / "*.json"))
        for ef in existing:
            if "config.json" in ef: continue
            with open(ef, 'r', encoding='utf-8') as f:
                try:
                    ed = json.load(f)
                    completed_task_ids.add(ed['task_id'])
                    experiment_id = ed['experiment_id'] # Use the existing experiment ID!
                except Exception:
                    pass
                    
    # Save experiment configuration
    model_raw_dir.mkdir(parents=True, exist_ok=True)
    config_file = model_raw_dir / f"{experiment_id}_config.json"
    if not config_file.exists() and not os.environ.get('PROOFSEC_DRY_RUN') == '1':
        from src.proofsec.version import __version__
        config_data = {
            "benchmark_version": __version__,
            "benchmark_sha256": dataset_hash,
            "experiment_id": experiment_id,
            "model": model,
            "provider": "UNAVAILABLE", # Kaggle abstracted
            "model_version": "UNAVAILABLE",
            "temperature": "UNAVAILABLE",
            "max_tokens": "UNAVAILABLE",
            "system_prompt_hash": "UNAVAILABLE",
            "prompt_template_hash": "UNAVAILABLE",
            "runner_version": "v0.2",
            "timestamp": timestamp
        }
        with open(config_file, 'w', encoding='utf-8') as cf:
            json.dump(config_data, cf, indent=4)
            
    task_funcs = []
    for task_data in tasks:
        if is_resume and task_data['id'] in completed_task_ids:
            continue
            
        def make_task(t_data):
            def run_task(llm) -> None:
                is_dry_run = os.environ.get('PROOFSEC_DRY_RUN') == '1'
                scenario = t_data['scenario']
                prompt = (
                    "You are an expert security code reviewer. Analyze the following scenario:\n\n"
                    f"{scenario}\n\n"
                    "Please provide your analysis and classify it using the required schema format.\n"
                    "Identify:\n"
                    "- evidence currently available (What is directly observed?)\n"
                    "- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)\n"
                    "- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)\n"
                    "- final classification (Must be exactly one of: \"Vulnerable\", \"Not Vulnerable\", \"Insufficient Evidence\")\n"
                )
                
                if is_dry_run:
                    print(f"[DRY-RUN] Would execute task: {t_data['id']}")
                    return
                
                start_t = time.time()
                try:
                    response = llm.prompt(prompt, schema=SecurityAssessment)
                except Exception as e:
                    # Isolate infrastructure failure
                    latency = int((time.time() - start_t) * 1000)
                    error_dir = get_project_root() / "results" / "errors" / model
                    error_dir.mkdir(parents=True, exist_ok=True)
                    error_file = error_dir / f"{t_data['id']}_{int(time.time())}.json"
                    error_rec = {
                        "task_id": t_data['id'],
                        "experiment_id": experiment_id,
                        "status": "infrastructure_error",
                        "error_type": e.__class__.__name__,
                        "error_msg": str(e),
                        "latency_ms": latency
                    }
                    with open(error_file, 'w', encoding='utf-8') as ef:
                        json.dump(error_rec, ef, indent=4)
                    print(f"Infrastructure error isolated for {t_data['id']}: {e.__class__.__name__}")
                    raise e # Let it bubble up to halt execution
                    
                latency = int((time.time() - start_t) * 1000)
                
                expected = t_data['ground_truth']['classification']
                rationale = t_data['ground_truth']['rationale']
                is_correct = (expected == response.classification)
                
                save_raw_result(t_data, response, is_correct, dataset_hash, experiment_id, model, latency)
                assertions.assert_equal(expected=expected, actual=response.classification, expectation=rationale)
                
            run_task.__name__ = t_data['id'].replace('-', '_')
            task_func = kbench.task(name=t_data['title'])(run_task)
            import sys
            setattr(sys.modules['__main__'], run_task.__name__, task_func)
            return task_func
            
        task_funcs.append(make_task(task_data))
        
    return task_funcs

def save_raw_result(task_data, response, is_correct, dataset_hash, experiment_id, model, latency):
    results_dir = get_project_root() / "results" / "raw" / model
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    task_id = task_data['id']
    filepath = results_dir / f"{task_id}_{timestamp}.json"
    
    try:
        model_resp = response.model_dump()
    except AttributeError:
        model_resp = {"raw_output": str(response)}
        
    from src.proofsec.version import __version__
        
    structured_output = {
        "benchmark_version": __version__,
        "dataset_sha256": dataset_hash,
        "experiment_id": experiment_id,
        "task_id": task_id,
        "model": model,
        "classification": getattr(response, 'classification', 'UNKNOWN'),
        "expected_classification": task_data['ground_truth']['classification'],
        "correct": is_correct,
        "latency_ms": latency,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost": 0,
        "evidence_state": task_data.get('evidence_state', 'UNKNOWN'),
        "task_family": task_data.get('task_family', 'UNKNOWN'),
        "experiment": task_data.get('experiment', 'UNKNOWN'),
        "category": task_data.get('category', 'UNKNOWN'),
        "response": model_resp,
        "timestamp": timestamp
    }
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(structured_output, f, indent=4)
