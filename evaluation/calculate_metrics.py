import json
import glob
import argparse
from pathlib import Path
from collections import defaultdict

def get_project_root():
    return Path(__file__).parent.parent

def calculate_metrics(results_dir=None, output_file=None):
    if results_dir is None:
        results_dir = get_project_root() / "results" / "raw"
    else:
        results_dir = Path(results_dir)
        
    files = glob.glob(str(results_dir / "*.json"))
    
    tasks_results = {}
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            tasks_results[data['task_id']] = data

    # Reload tasks to get full metadata structure
    tasks_dir = get_project_root() / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    tasks_meta = {}
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            t = json.load(file)
            tasks_meta[t['id']] = t
            
    metrics = {
        "overall_accuracy": 0,
        "total_tasks": len(tasks_results),
        "correct": 0,
        "classes": {
            "Vulnerable": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "Not Vulnerable": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "Insufficient Evidence": {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        },
        "by_domain": defaultdict(lambda: {"correct": 0, "total": 0}),
        "by_evidence_state": defaultdict(lambda: {"correct": 0, "total": 0}),
        "evidence_sensitivity": {"flips": 0, "valid_pairs": 0, "appropriate_flips": 0, "flip_errors": 0, "flip_misses": 0},
        "authority_bias": {"flips": 0, "valid_pairs": 0},
        "terminology_sensitivity": {"flips": 0, "valid_pairs": 0},
        "contradiction_accuracy": {"correct": 0, "total": 0},
        "ladder_monotonicity": {"monotonic_ladders": 0, "total_ladders": 0}
    }
    
    # 1. Base Metrics
    for tid, data in tasks_results.items():
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
            
        if expected in metrics['classes']:
            for cls in metrics['classes'].keys():
                if expected == cls and actual == cls:
                    metrics['classes'][cls]['tp'] += 1
                elif expected == cls and actual != cls:
                    metrics['classes'][cls]['fn'] += 1
                elif expected != cls and actual == cls:
                    metrics['classes'][cls]['fp'] += 1
                else:
                    metrics['classes'][cls]['tn'] += 1
                    
        # Contradiction
        if data.get('task_family') == 'contradiction':
            metrics['contradiction_accuracy']['total'] += 1
            if correct:
                metrics['contradiction_accuracy']['correct'] += 1

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
    
    # 2. Paired Metrics (One Fact Flip, Authority Bias, Terminology)
    processed_pairs = set()
    for tid, meta in tasks_meta.items():
        if meta.get('task_family') == 'one_fact_flip' and tid in tasks_results:
            pid = meta.get('paired_task_id')
            if pid and pid in tasks_results and pid not in processed_pairs:
                processed_pairs.add(tid)
                processed_pairs.add(pid)
                
                exp = meta.get('experiment', '')
                res_a = tasks_results[tid]
                res_b = tasks_results[pid]
                
                changed = res_a['classification'] != res_b['classification']
                should_change = res_a['expected_classification'] != res_b['expected_classification']
                
                if 'authority_bias' in exp:
                    metrics['authority_bias']['valid_pairs'] += 1
                    if changed: metrics['authority_bias']['flips'] += 1
                elif 'terminology' in exp:
                    metrics['terminology_sensitivity']['valid_pairs'] += 1
                    if changed: metrics['terminology_sensitivity']['flips'] += 1
                else:
                    metrics['evidence_sensitivity']['valid_pairs'] += 1
                    if changed:
                        metrics['evidence_sensitivity']['flips'] += 1
                        if should_change and res_a['correct'] and res_b['correct']:
                            metrics['evidence_sensitivity']['appropriate_flips'] += 1
                        elif not should_change:
                            metrics['evidence_sensitivity']['flip_errors'] += 1
                    else:
                        if should_change:
                            metrics['evidence_sensitivity']['flip_misses'] += 1

    # 3. Evidence Ladders Monotonicity
    ladders = defaultdict(list)
    for tid, meta in tasks_meta.items():
        if meta.get('task_family') == 'evidence_ladder' and tid in tasks_results:
            base_id = tid.rsplit("-l", 1)[0]
            ladders[base_id].append((meta['ladder_stage'], tasks_results[tid]['classification']))
            
    for base_id, stages in ladders.items():
        stages.sort(key=lambda x: x[0]) # sort by stage
        metrics['ladder_monotonicity']['total_ladders'] += 1
        
        # A simple check: if stage 1 is 'Vulnerable' and stage 4 is 'Insufficient Evidence', it's non-monotonic
        # A strict check is that confidence/severity should not decrease.
        # We approximate this by checking if the expected progression is maintained (weak -> decisive).
        # We will assume monotonic if it doesn't revert from Vulnerable to Insufficient.
        is_monotonic = True
        reached_vuln = False
        for s, cls in stages:
            if cls == 'Vulnerable':
                reached_vuln = True
            if reached_vuln and cls == 'Insufficient Evidence':
                is_monotonic = False
                
        if is_monotonic:
            metrics['ladder_monotonicity']['monotonic_ladders'] += 1

    # Save metrics
    if output_file is None:
        metrics_dir = get_project_root() / "results" / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        out_path = metrics_dir / "latest_metrics.json"
    else:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
    with open(out_path, 'w', encoding='utf-8') as file:
        json.dump(metrics, file, indent=4)
        
    print(f"Metrics calculated for {metrics['total_tasks']} tasks.")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', type=str, help='Directory containing raw results JSONs')
    parser.add_argument('--output-file', type=str, help='Path to output JSON file')
    args = parser.parse_args()
    
    calculate_metrics(args.results_dir, args.output_file)
