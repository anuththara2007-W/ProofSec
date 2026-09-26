import json
import glob
from pathlib import Path
import os
import time

try:
    import kaggle_benchmarks as kbench
    from kaggle_benchmarks import assertions
except ImportError:
    kbench = None
    assertions = None

from src.proofsec.schemas import SecurityAssessment

def get_project_root():
    return Path(__file__).parent.parent.parent

def load_tasks(task_filter=None, category_filter=None, experiment_filter=None):
    tasks_dir = get_project_root() / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    
    tasks = []
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                t = json.load(file)
            except Exception as e:
                print(f"Failed to load JSON {f}: {e}")
                continue
                
            if task_filter and t.get('id') != task_filter:
                continue
            if category_filter and t.get('category') != category_filter:
                continue
            if experiment_filter and t.get('experiment') != experiment_filter:
                continue
                
            tasks.append(t)
    return tasks

def register_kbench_tasks():
    if not kbench:
        print("Warning: kaggle_benchmarks not installed or not found.")
        return
        
    task_filter = os.environ.get('PROOFSEC_TASK')
    category_filter = os.environ.get('PROOFSEC_CATEGORY')
    experiment_filter = os.environ.get('PROOFSEC_EXPERIMENT')
        
    tasks = load_tasks(task_filter, category_filter, experiment_filter)
    
    for task_data in tasks:
        def make_task(t_data):
            def run_task(llm) -> None:
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
                
                # Model prompt does NOT contain expected answer!
                response = llm.prompt(prompt, schema=SecurityAssessment)
                
                expected = t_data['ground_truth']['classification']
                rationale = t_data['ground_truth']['rationale']
                
                # Save raw response
                save_raw_result(t_data['id'], response)
                
                # Deterministic check
                assertions.assert_equal(expected=expected, actual=response.classification, expectation=rationale)
                
            run_task.__name__ = t_data['id'].replace('-', '_')
            return kbench.task(name=t_data['title'])(run_task)
            
        make_task(task_data)

def save_raw_result(task_id, response):
    results_dir = get_project_root() / "results" / "raw"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    filepath = results_dir / f"{task_id}_{timestamp}.json"
    
    try:
        data = response.model_dump()
    except AttributeError:
        data = str(response)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
