import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import kaggle_benchmarks as kbench
from src.proofsec.runner import register_kbench_tasks

# This file is executed directly by Kaggle Benchmark CLI.
task_funcs = register_kbench_tasks()

if __name__ == "__main__":
    for t_func in task_funcs:
        t_func.run(kbench.llm)
