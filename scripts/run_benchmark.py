import argparse
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
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without API calls")
    
    args, unknown = parser.parse_known_args()
    
    if args.task: os.environ['PROOFSEC_TASK'] = args.task
    if args.category: os.environ['PROOFSEC_CATEGORY'] = args.category
    if args.experiment: os.environ['PROOFSEC_EXPERIMENT'] = args.experiment
    if args.resume: os.environ['PROOFSEC_RESUME'] = '1'
    if args.dry_run: os.environ['PROOFSEC_DRY_RUN'] = '1'
    
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
        print(f"\n{'='*50}\nStarting evaluation for model: {model}\n{'='*50}")
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
