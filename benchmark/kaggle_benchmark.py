import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.proofsec.runner import register_kbench_tasks

# This file is executed directly by Kaggle Benchmark CLI.
# e.g., python benchmark/kaggle_benchmark.py
register_kbench_tasks()
