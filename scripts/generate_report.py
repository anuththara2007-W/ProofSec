import json
from pathlib import Path
import sys
def get_project_root():
    return Path(__file__).parent.parent

sys.path.insert(0, str(get_project_root()))
from src.proofsec.version import __version__

def generate_report():
    metrics_file = get_project_root() / "results" / "metrics" / "latest_metrics.json"
    if not metrics_file.exists():
        print("No metrics found. Run calculate_metrics.py first.")
        return
        
    with open(metrics_file, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
        
    report = f"""# ProofSec Research Report

## Executive Summary
- **Benchmark Version**: {__version__}
- **Number of Tasks**: {metrics['total_tasks']}
- **Models Evaluated**: 1 (gemini-3.5-flash default)
- **Total Evaluations**: {metrics['total_tasks']}
- **Overall Accuracy**: {metrics['overall_accuracy']:.2%}
- **Macro F1**: {metrics['macro_f1']:.2f}

## Research Questions
- Can an AI security model distinguish a plausible security signal from a security vulnerability that is actually demonstrated by sufficient evidence, while remaining consistent when one decisive fact changes?

## Results by Security Domain
| Domain | Tasks | Accuracy |
|--------|-------|----------|
"""
    
    for domain, stats in metrics['by_domain'].items():
        acc = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        report += f"| {domain} | {stats['total']} | {acc:.2%} |\n"
        
    report += "\n## Results by Evidence State\n"
    report += "| Evidence State | Tasks | Accuracy |\n"
    report += "|----------------|-------|----------|\n"
    
    for state, stats in metrics['by_evidence_state'].items():
        acc = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        report += f"| {state} | {stats['total']} | {acc:.2%} |\n"
        
    report += "\n## Per-Class Performance\n"
    report += "| Class | Precision | Recall | F1 |\n"
    report += "|-------|-----------|--------|----|\n"
    for cls, stats in metrics['classes'].items():
        report += f"| {cls} | {stats['precision']:.2f} | {stats['recall']:.2f} | {stats['f1']:.2f} |\n"
        
    reports_dir = get_project_root() / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    with open(reports_dir / "latest_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Report generated at {reports_dir / 'latest_report.md'}")

if __name__ == "__main__":
    generate_report()
