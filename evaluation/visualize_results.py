import json
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent

def generate_visualizations():
    metrics_file = get_project_root() / "results" / "metrics" / "latest_metrics.json"
    if not metrics_file.exists():
        print("No metrics found.")
        return
        
    with open(metrics_file, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
        
    figures_dir = get_project_root() / "results" / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Confusion Matrix (Markdown Table)
    cm = metrics['classes']
    cm_md = "### Confusion Matrix\n\n"
    cm_md += "| Actual \\ Expected | Vulnerable | Not Vulnerable | Insufficient Evidence |\n"
    cm_md += "|---|---|---|---|\n"
    
    def get_cell(actual, expected):
        if actual == expected:
            return cm[actual]['tp']
        else:
            return "N/A" # Simplified for this matrix
            
    # Note: For a true confusion matrix we need the exact pairs, but since we didn't store the full N*N grid, 
    # we'll represent the Precision/Recall/F1 table instead as a core visualization
    
    cm_md = "### Class Metrics\n\n"
    cm_md += "| Class | TP | FP | FN | Precision | Recall | F1 |\n"
    cm_md += "|-------|----|----|----|-----------|--------|----|\n"
    for cls, stats in cm.items():
        cm_md += f"| {cls} | {stats['tp']} | {stats['fp']} | {stats['fn']} | {stats.get('precision',0):.2f} | {stats.get('recall',0):.2f} | {stats.get('f1',0):.2f} |\n"
        
    with open(figures_dir / "class_metrics.md", "w") as f:
        f.write(cm_md)

    # 2. Accuracy by Security Domain (Mermaid Bar Chart)
    domain_md = "### Accuracy by Domain\n\n```mermaid\nxychart-beta\n    title \"Accuracy by Domain\"\n"
    domains = []
    accs = []
    for domain, stats in metrics['by_domain'].items():
        domains.append(f'"{domain}"')
        acc = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        accs.append(f"{acc:.0f}")
        
    if domains:
        domain_md += f"    x-axis [{', '.join(domains)}]\n"
        domain_md += "    y-axis \"Accuracy (%)\" 0 --> 100\n"
        domain_md += f"    bar [{', '.join(accs)}]\n"
    domain_md += "```\n"
    
    with open(figures_dir / "domain_accuracy.md", "w") as f:
        f.write(domain_md)
        
    # 3. Accuracy by Evidence State (Mermaid Bar Chart)
    state_md = "### Accuracy by Evidence State\n\n```mermaid\nxychart-beta\n    title \"Accuracy by Evidence State\"\n"
    states = []
    s_accs = []
    for state, stats in metrics['by_evidence_state'].items():
        states.append(f'"{state}"')
        acc = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        s_accs.append(f"{acc:.0f}")
        
    if states:
        state_md += f"    x-axis [{', '.join(states)}]\n"
        state_md += "    y-axis \"Accuracy (%)\" 0 --> 100\n"
        state_md += f"    bar [{', '.join(s_accs)}]\n"
    state_md += "```\n"
    
    with open(figures_dir / "state_accuracy.md", "w") as f:
        f.write(state_md)
        
    print(f"Visualizations generated in {figures_dir}")

if __name__ == "__main__":
    generate_visualizations()
