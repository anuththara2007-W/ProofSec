import json
import csv
from pathlib import Path

def compute_metrics():
    root = Path(__file__).parent.parent
    tasks_dir = root / 'tasks'
    res_dir = root / 'results' / 'raw' / 'gemini-3.5-flash'
    
    # Load tasks
    tasks = {}
    for f in tasks_dir.glob('**/*.json'):
        with open(f, 'r', encoding='utf-8') as file:
            d = json.load(file)
            tasks[d['id']] = d

    # Load responses (keep latest)
    responses = {}
    for f in sorted(res_dir.glob('*.json')):
        with open(f, 'r', encoding='utf-8') as file:
            d = json.load(file)
            responses[d['task_id']] = d
            
def compute_metrics_from_data(tasks, responses):
    if not responses:
        return None

    # Basic metrics
    correct = 0
    pvr_eligible = 0
    pvr_failures = 0
    
    for t_id, res in responses.items():
        if t_id not in tasks:
            continue
        t = tasks[t_id]
        expected = t['ground_truth']['classification']
        observed = res['classification']
        
        if expected == observed:
            correct += 1
            
        if expected != 'Vulnerable':
            pvr_eligible += 1
            if observed == 'Vulnerable':
                pvr_failures += 1
                
    acc = correct / len(responses)
    pvr = pvr_failures / pvr_eligible if pvr_eligible else 0
    
    # Pair metrics
    flip_pairs = 0
    flip_consistent = 0
    flip_miss = 0
    flip_err = 0
    
    auth_pairs = 0
    auth_err = 0
    
    term_pairs = 0
    term_err = 0
    
    for t_id, t in tasks.items():
        if 'paired_task_id' in t and t['paired_task_id'] is not None:
            p_id = t['paired_task_id']
            if t_id in responses and p_id in responses:
                # We only count each pair once. We'll only process if t_id < p_id
                if t_id < p_id:
                    res1 = responses[t_id]['classification']
                    res2 = responses[p_id]['classification']
                    exp1 = tasks[t_id]['ground_truth']['classification']
                    exp2 = tasks[p_id]['ground_truth']['classification']
                    
                    family = t.get('task_family', '')
                    
                    if 'flip' in t_id or family == 'one_fact_flip':
                        flip_pairs += 1
                        if res1 == exp1 and res2 == exp2:
                            flip_consistent += 1
                        
                        if exp1 != exp2 and res1 == res2:
                            flip_miss += 1
                            
                        if exp1 == exp2 and res1 != res2:
                            flip_err += 1
                            
                    if 'authbias' in t_id:
                        auth_pairs += 1
                        if res1 != res2:
                            auth_err += 1
                            
                    if 'term' in t_id:
                        term_pairs += 1
                        if res1 != res2:
                            term_err += 1
                            
    flip_miss_rate = flip_miss / flip_pairs if flip_pairs else 0
    flip_err_rate = flip_err / flip_pairs if flip_pairs else 0
    pair_consistency = flip_consistent / flip_pairs if flip_pairs else 0
    auth_bias = auth_err / auth_pairs if auth_pairs else 0
    term_bias = term_err / term_pairs if term_pairs else 0
    
    return {
        'acc': acc,
        'pvr': pvr,
        'flip_miss_rate': flip_miss_rate,
        'flip_err_rate': flip_err_rate,
        'pair_consistency': pair_consistency,
        'auth_bias': auth_bias,
        'term_bias': term_bias
    }

def compute_metrics():
    root = Path(__file__).parent.parent
    tasks_dir = root / 'tasks'
    res_dir = root / 'results' / 'raw' / 'gemini-3.5-flash'
    
    # Load tasks
    tasks = {}
    for f in tasks_dir.glob('**/*.json'):
        with open(f, 'r', encoding='utf-8') as file:
            d = json.load(file)
            tasks[d['id']] = d

    # Load responses (keep latest)
    responses = {}
    for f in sorted(res_dir.glob('*.json')):
        with open(f, 'r', encoding='utf-8') as file:
            d = json.load(file)
            responses[d['task_id']] = d
            
    m = compute_metrics_from_data(tasks, responses)
    if not m:
        print("No responses found.")
        return
        
    out_csv = root / 'results' / 'metrics' / 'model_summary.csv'
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'model', 'experiment_id', 'tasks_total', 'tasks_completed', 'status',
            'accuracy', 'pvr', 'flip_miss_rate', 'flip_error_rate', 
            'pair_consistency', 'authority_bias', 'terminology_sensitivity', 'confidence_status'
        ])
        writer.writerow([
            'gemini-3.5-flash', 'v0_2_gemini-3.5-flash_1727357497', 110, len(responses), 'PARTIAL',
            f"{m['acc']:.4f}", f"{m['pvr']:.4f}", f"{m['flip_miss_rate']:.4f}", f"{m['flip_err_rate']:.4f}",
            f"{m['pair_consistency']:.4f}", f"{m['auth_bias']:.4f}", f"{m['term_bias']:.4f}", 'UNAVAILABLE'
        ])
        
    print(f"Recomputation complete. Saved to {out_csv}")
    print(f"Acc: {m['acc']:.4f}, PVR: {m['pvr']:.4f}")
    
if __name__ == '__main__':
    compute_metrics()
