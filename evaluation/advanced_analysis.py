import json
from pathlib import Path

def advanced_analysis():
    root = Path(__file__).parent.parent
    results_dir = root / "results" / "raw" / "gemini-3.5-flash"
    
    if not results_dir.exists():
        print("No raw results found.")
        return
        
    tasks_dir = root / "tasks"
    
    # Load all tasks
    benchmark = {}
    for task_file in tasks_dir.glob("**/*.json"):
        with open(task_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
            benchmark[d['id']] = d
            
    # Load all raw responses
    responses = {}
    for res_file in results_dir.glob("*.json"):
        with open(res_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
            responses[d['task_id']] = d
            
    # Matrix counting
    # PVR by evidence state
    pvr_eligible = 0
    pvr_failures = 0
    
    evidence_matrix = {
        'WEAK': {'Expected': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}, 'Observed': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}},
        'PARTIAL': {'Expected': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}, 'Observed': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}},
        'DECISIVE': {'Expected': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}, 'Observed': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}},
        'CONTRADICTORY': {'Expected': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}, 'Observed': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}},
        'NEGATIVE': {'Expected': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}, 'Observed': {'Insufficient Evidence': 0, 'Not Vulnerable': 0, 'Vulnerable': 0}},
    }
    
    flip_matrix = {
        'Correct Transition': 0,
        'Missed Transition': 0,
        'Incorrect Transition': 0,
    }
    
    for t_id, res in responses.items():
        t_data = benchmark[t_id]
        expected = t_data['ground_truth']['classification']
        observed = res['classification']
        ev_state = t_data['evidence_state']
        
        if ev_state in evidence_matrix:
            evidence_matrix[ev_state]['Expected'][expected] += 1
            evidence_matrix[ev_state]['Observed'][observed] += 1
            
        if expected != 'Vulnerable':
            pvr_eligible += 1
            if observed == 'Vulnerable':
                pvr_failures += 1
                
    out_data = {
        'pvr_analysis': {
            'eligible': pvr_eligible,
            'failures': pvr_failures,
            'rate': pvr_failures / pvr_eligible if pvr_eligible > 0 else 0
        },
        'evidence_matrix': evidence_matrix,
        'flip_matrix': flip_matrix # Placeholder for full pairwise logic
    }
    
    out_file = root / "results" / "reports" / "advanced_analysis.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, indent=2)
        
    print("Advanced analysis complete. Saved to results/reports/advanced_analysis.json")
    
if __name__ == "__main__":
    advanced_analysis()
