import json
import glob
from pathlib import Path
from collections import defaultdict

def get_project_root():
    return Path(__file__).parent.parent

def calculate_metrics():
    results_dir = get_project_root() / "results" / "raw"
    files = glob.glob(str(results_dir / "*.json"))
    
    metrics = {
        "overall_accuracy": 0,
        "total_tasks": len(files),
        "correct": 0,
        "classes": {
            "Vulnerable": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "Not Vulnerable": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "Insufficient Evidence": {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        },
        "by_domain": defaultdict(lambda: {"correct": 0, "total": 0}),
        "by_evidence_state": defaultdict(lambda: {"correct": 0, "total": 0})
    }
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        actual = data.get('classification')
        expected = data.get('expected_classification')
        correct = data.get('correct', False)
        
        domain = data.get('category', 'unknown')
        evidence_state = data.get('evidence_state', 'unknown')
        
        metrics['by_domain'][domain]['total'] += 1
        metrics['by_evidence_state'][evidence_state]['total'] += 1
        
        if correct:
            metrics['correct'] += 1
            metrics['by_domain'][domain]['correct'] += 1
            metrics['by_evidence_state'][evidence_state]['correct'] += 1
            
        for cls in metrics['classes'].keys():
            if expected == cls and actual == cls:
                metrics['classes'][cls]['tp'] += 1
            elif expected == cls and actual != cls:
                metrics['classes'][cls]['fn'] += 1
            elif expected != cls and actual == cls:
                metrics['classes'][cls]['fp'] += 1
            else:
                metrics['classes'][cls]['tn'] += 1

    if metrics['total_tasks'] > 0:
        metrics['overall_accuracy'] = metrics['correct'] / metrics['total_tasks']
        
    for cls, stats in metrics['classes'].items():
        tp = stats['tp']
        fp = stats['fp']
        fn = stats['fn']
        
        stats['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0
        stats['recall'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        stats['f1'] = 2 * (stats['precision'] * stats['recall']) / (stats['precision'] + stats['recall']) if (stats['precision'] + stats['recall']) > 0 else 0

    f1_sum = sum(stats['f1'] for stats in metrics['classes'].values())
    metrics['macro_f1'] = f1_sum / 3 if metrics['total_tasks'] > 0 else 0
    
    # Save metrics
    metrics_dir = get_project_root() / "results" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    with open(metrics_dir / "latest_metrics.json", 'w', encoding='utf-8') as file:
        json.dump(metrics, file, indent=4)
        
    print(f"Metrics calculated for {metrics['total_tasks']} tasks.")
    print(f"Overall Accuracy: {metrics['overall_accuracy']:.2%}")
    print(f"Macro F1: {metrics['macro_f1']:.2f}")

if __name__ == "__main__":
    calculate_metrics()
