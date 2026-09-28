import json
from pathlib import Path
import math

def get_project_root():
    return Path(__file__).parent.parent

def calculate_confidence_interval(successes, n, z=1.96):
    if n == 0:
        return 0, 0
    p = successes / n
    margin = z * math.sqrt((p * (1 - p)) / n)
    return max(0, p - margin), min(1, p + margin)

def analyze_statistics():
    metrics_file = get_project_root() / "results" / "metrics" / "latest_metrics.json"
    if not metrics_file.exists():
        print("No metrics found.")
        return
        
    with open(metrics_file, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
        
    stats = {}
    
    acc_n = metrics['total_tasks']
    acc_succ = metrics['correct']
    ci_low, ci_high = calculate_confidence_interval(acc_succ, acc_n)
    stats['overall_accuracy_ci'] = (ci_low, ci_high)
    
    sens_n = metrics['evidence_sensitivity']['valid_pairs']
    sens_succ = metrics['evidence_sensitivity']['flips']
    ci_low, ci_high = calculate_confidence_interval(sens_succ, sens_n)
    stats['evidence_sensitivity_ci'] = (ci_low, ci_high)
    
    auth_n = metrics['authority_bias']['valid_pairs']
    auth_succ = metrics['authority_bias']['flips']
    ci_low, ci_high = calculate_confidence_interval(auth_succ, auth_n)
    stats['authority_bias_ci'] = (ci_low, ci_high)
    
    stats_file = get_project_root() / "results" / "metrics" / "statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
        
    print(f"Statistical analysis generated at {stats_file}")

if __name__ == "__main__":
    analyze_statistics()
