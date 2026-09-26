import os
from pathlib import Path

def update_run_benchmark():
    content = """import argparse
import os
import subprocess
import sys
import json
from pathlib import Path
import time

def main():
    parser = argparse.ArgumentParser(description="Run the ProofSec benchmark.")
    parser.add_argument("--task", help="Run a specific task by ID")
    parser.add_argument("--category", help="Run a specific category")
    parser.add_argument("--experiment", help="Run a specific experiment")
    parser.add_argument("--all", action="store_true", help="Run all tasks")
    parser.add_argument("--model", help="Specify a single model to run")
    parser.add_argument("--all-models", action="store_true", help="Run all available models")
    parser.add_argument("--resume", action="store_true", help="Resume an existing run (skip completed tasks)")
    parser.add_argument("--fresh", action="store_true", help="Start a fresh run (default behavior without --resume)")
    
    args, unknown = parser.parse_known_args()
    
    if args.task: os.environ['PROOFSEC_TASK'] = args.task
    if args.category: os.environ['PROOFSEC_CATEGORY'] = args.category
    if args.experiment: os.environ['PROOFSEC_EXPERIMENT'] = args.experiment
    if args.resume: os.environ['PROOFSEC_RESUME'] = '1'
    
    root_dir = Path(__file__).parent.parent
    
    with open(root_dir / 'benchmark' / 'models.json', 'r', encoding='utf-8') as f:
        models_cfg = json.load(f)
        
    models_to_run = []
    if args.all_models:
        models_to_run = models_cfg.get('available_models', [])
    elif args.model:
        models_to_run = [args.model]
    else:
        models_to_run = [models_cfg.get('default_model', 'gemini-3.5-flash')]
        
    benchmark_script = root_dir / "benchmark" / "kaggle_benchmark.py"
    
    # Generate timestamp for fresh runs
    timestamp = int(time.time())
    
    for model in models_to_run:
        print(f"\\n{'='*50}\\nStarting evaluation for model: {model}\\n{'='*50}")
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PROOFSEC_MODEL'] = model
        
        # If fresh, we create a new experiment ID marker.
        # But kaggle benchmarks uses global config. We will just pass the model name.
        if not args.resume:
            env['PROOFSEC_FRESH_TIMESTAMP'] = str(timestamp)
            
        cmd = [sys.executable, str(benchmark_script)] + unknown
        
        # NOTE: For real kaggle benchmarking, we might need to pass the model to kbench.
        # However, kbench usually determines model via kaggle_benchmarks config.
        # For this simulation/environment, we assume it's passed or handled.
        # We will add it to unknown args if kbench supports it.
        # cmd.extend(['--model', model])
        
        result = subprocess.run(cmd, env=env)
        if result.returncode != 0:
            print(f"Execution failed or interrupted for model {model}.")

if __name__ == "__main__":
    main()
"""
    with open(Path(__file__).parent.parent / "scripts" / "run_benchmark.py", "w", encoding="utf-8") as f:
        f.write(content)

def update_runner():
    content = """import json
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
    return hashlib.sha256(task_string.encode('utf-8')).hexdigest()

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
            with open(ef, 'r', encoding='utf-8') as f:
                try:
                    ed = json.load(f)
                    completed_task_ids.add(ed['task_id'])
                    experiment_id = ed['experiment_id'] # Use the existing experiment ID!
                except Exception:
                    pass
    
    task_funcs = []
    for task_data in tasks:
        if is_resume and task_data['id'] in completed_task_ids:
            continue
            
        def make_task(t_data):
            def run_task(llm) -> None:
                scenario = t_data['scenario']
                prompt = (
                    "You are an expert security code reviewer. Analyze the following scenario:\\n\\n"
                    f"{scenario}\\n\\n"
                    "Please provide your analysis and classify it using the required schema format.\\n"
                    "Identify:\\n"
                    "- evidence currently available (What is directly observed?)\\n"
                    "- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)\\n"
                    "- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)\\n"
                    "- final classification (Must be exactly one of: \\"Vulnerable\\", \\"Not Vulnerable\\", \\"Insufficient Evidence\\")\\n"
                )
                
                start_t = time.time()
                response = llm.prompt(prompt, schema=SecurityAssessment)
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
"""
    with open(Path(__file__).parent.parent / "src" / "proofsec" / "runner.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_run_benchmark()
    update_runner()
    print("Runner upgraded successfully.")
