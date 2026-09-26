import json
import glob
from pathlib import Path
from collections import defaultdict
import os

def get_project_root():
    return Path(__file__).parent.parent

def calculate_metrics():
    root = get_project_root()
    models_dir = root / "results" / "raw"
    if not models_dir.exists():
        return
        
    models = [d.name for d in models_dir.iterdir() if d.is_dir()]
    
    # Load tasks metadata
    tasks_dir = root / "tasks"
    task_files = glob.glob(str(tasks_dir / "**/*.json"), recursive=True)
    tasks_meta = {}
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            t = json.load(file)
            tasks_meta[t['id']] = t
            
    comparison = {
        "benchmark": "ProofSec v0.2",
        "models": []
    }

    for model in models:
        files = glob.glob(str(models_dir / model / "*.json"))
        tasks_results = {}
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                tasks_results[data['task_id']] = data

        metrics = {
            "model": model,
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
            "ladder_monotonicity": {"monotonic_ladders": 0, "total_ladders": 0},
            "pvr": {"premature_vulnerability_claims": 0, "eligible_cases": 0}
        }
        
        # 1. Base Metrics & PVR
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
                    
            # PVR calculation: Eligible cases are those where the true state is NOT Vulnerable
            # (i.e. Insufficient Evidence or Not Vulnerable).
            if expected != "Vulnerable":
                metrics['pvr']['eligible_cases'] += 1
                if actual == "Vulnerable":
                    metrics['pvr']['premature_vulnerability_claims'] += 1

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
        off_analysis = []
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
                                
                    off_analysis.append({
                        "pair_id": f"{tid}_{pid}",
                        "task_a": tid,
                        "task_b": pid,
                        "expected_transition": f"{res_a['expected_classification']} -> {res_b['expected_classification']}",
                        "observed_transition": f"{res_a['classification']} -> {res_b['classification']}",
                        "correct": should_change == changed
                    })

        # Save off analysis
        metrics_dir = root / "results" / "metrics" / model
        metrics_dir.mkdir(parents=True, exist_ok=True)
        with open(metrics_dir / "one_fact_flip_analysis.json", 'w', encoding='utf-8') as file:
            json.dump(off_analysis, file, indent=4)

        # 3. Evidence Ladders Monotonicity
        ladders = defaultdict(list)
        for tid, meta in tasks_meta.items():
            if meta.get('task_family') == 'evidence_ladder' and tid in tasks_results:
                base_id = tid.rsplit("-l", 1)[0]
                ladders[base_id].append((meta['ladder_stage'], tasks_results[tid]['classification']))
                
        for base_id, stages in ladders.items():
            stages.sort(key=lambda x: x[0])
            metrics['ladder_monotonicity']['total_ladders'] += 1
            
            is_monotonic = True
            reached_vuln = False
            for s, cls in stages:
                if cls == 'Vulnerable':
                    reached_vuln = True
                if reached_vuln and cls == 'Insufficient Evidence':
                    is_monotonic = False
                    
            if is_monotonic:
                metrics['ladder_monotonicity']['monotonic_ladders'] += 1

        with open(metrics_dir / "latest_metrics.json", 'w', encoding='utf-8') as file:
            json.dump(metrics, file, indent=4)
            
        comparison['models'].append({
            "model": model,
            "task_count": metrics['total_tasks'],
            "accuracy": metrics['overall_accuracy'],
            "macro_f1": metrics['macro_f1'],
            "evidence_sensitivity": metrics['evidence_sensitivity']['flips'] / max(1, metrics['evidence_sensitivity']['valid_pairs']),
            "flip_miss_rate": metrics['evidence_sensitivity']['flip_misses'] / max(1, metrics['evidence_sensitivity']['valid_pairs']),
            "authority_bias_rate": metrics['authority_bias']['flips'] / max(1, metrics['authority_bias']['valid_pairs']),
            "terminology_sensitivity_rate": metrics['terminology_sensitivity']['flips'] / max(1, metrics['terminology_sensitivity']['valid_pairs']),
            "contradiction_accuracy": metrics['contradiction_accuracy']['correct'] / max(1, metrics['contradiction_accuracy']['total']),
            "ladder_monotonicity": metrics['ladder_monotonicity']['monotonic_ladders'] / max(1, metrics['ladder_monotonicity']['total_ladders']),
            "premature_vulnerability_rate": metrics['pvr']['premature_vulnerability_claims'] / max(1, metrics['pvr']['eligible_cases'])
        })

    with open(root / "results" / "metrics" / "model_comparison.json", 'w', encoding='utf-8') as file:
        json.dump(comparison, file, indent=4)

if __name__ == "__main__":
    calculate_metrics()
