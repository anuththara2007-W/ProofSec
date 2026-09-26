import argparse
import os
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run the ProofSec benchmark.")
    parser.add_argument("--task", help="Run a specific task by ID (e.g., task-001-idor-bola-evidence-test)")
    parser.add_argument("--category", help="Run a specific category (e.g., idor)")
    parser.add_argument("--experiment", help="Run a specific experiment (e.g., migrated_baseline)")
    parser.add_argument("--all", action="store_true", help="Run all tasks")
    
    args, unknown = parser.parse_known_args()
    
    if args.task:
        os.environ['PROOFSEC_TASK'] = args.task
    if args.category:
        os.environ['PROOFSEC_CATEGORY'] = args.category
    if args.experiment:
        os.environ['PROOFSEC_EXPERIMENT'] = args.experiment
        
    root_dir = Path(__file__).parent.parent
    benchmark_script = root_dir / "benchmark" / "kaggle_benchmark.py"
    
    cmd = [sys.executable, str(benchmark_script)] + unknown
    
    # We must explicitly set PYTHONIOENCODING for Windows
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
