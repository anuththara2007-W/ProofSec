import json
from pathlib import Path
import glob

def get_project_root():
    return Path(__file__).parent.parent

def analyze_surprises():
    root = get_project_root()
    models_dir = root / "results" / "raw"
    if not models_dir.exists():
        return
        
    models = [d.name for d in models_dir.iterdir() if d.is_dir()]
    
    surprises = []
    
    for model in models:
        metrics_file = root / "results" / "metrics" / model / "one_fact_flip_analysis.json"
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                pairs = json.load(f)
                for p in pairs:
                    if not p['correct']:
                        surprises.append(f"[{model}] Surprise in OFF Pair {p['pair_id']}: Expected {p['expected_transition']} but observed {p['observed_transition']}")
                        
        # Check PVR surprises
        files = glob.glob(str(models_dir / model / "*.json"))
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data['expected_classification'] != 'Vulnerable' and data['classification'] == 'Vulnerable':
                    surprises.append(f"[{model}] PVR Surprise in Task {data['task_id']}: Prematurely claimed Vulnerable on {data['evidence_state']} evidence.")
                    
    reports_dir = root / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "surprising_cases.md", 'w', encoding='utf-8') as f:
        f.write("# ProofSec Surprising Cases\\n\\n")
        for s in surprises:
            f.write(f"- {s}\\n")
            
    print("Surprises analyzed.")

if __name__ == "__main__":
    analyze_surprises()
