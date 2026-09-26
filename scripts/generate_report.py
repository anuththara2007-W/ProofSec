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
        
    def safe_pct(num, den):
        return f"{num/den:.2%}" if den > 0 else "N/A"
        
    report = f"""# ProofSec Research Report (Phase 2)

## Executive Summary
- **Benchmark Version**: {__version__}
- **Number of Tasks Evaluated**: {metrics['total_tasks']}
- **Models Evaluated**: 1 (gemini-3.5-flash)
- **Total Evaluations**: {metrics['total_tasks']}
- **Overall Accuracy**: {metrics['overall_accuracy']:.2%}
- **Macro F1**: {metrics['macro_f1']:.2f}

## Core Experimental Findings

| Metric | Result | Denominator |
|--------|--------|-------------|
| **Evidence Sensitivity** | {safe_pct(metrics['evidence_sensitivity']['flips'], metrics['evidence_sensitivity']['valid_pairs'])} | {metrics['evidence_sensitivity']['valid_pairs']} valid pairs |
| **Appropriate Sensitivity** | {safe_pct(metrics['evidence_sensitivity']['appropriate_flips'], metrics['evidence_sensitivity']['valid_pairs'])} | {metrics['evidence_sensitivity']['valid_pairs']} valid pairs |
| **Flip Error Rate** | {safe_pct(metrics['evidence_sensitivity']['flip_errors'], metrics['evidence_sensitivity']['valid_pairs'])} | {metrics['evidence_sensitivity']['valid_pairs']} valid pairs |
| **Flip Miss Rate** | {safe_pct(metrics['evidence_sensitivity']['flip_misses'], metrics['evidence_sensitivity']['valid_pairs'])} | {metrics['evidence_sensitivity']['valid_pairs']} valid pairs |
| **Authority Bias Rate** | {safe_pct(metrics['authority_bias']['flips'], metrics['authority_bias']['valid_pairs'])} | {metrics['authority_bias']['valid_pairs']} matched pairs |
| **Terminology Sensitivity** | {safe_pct(metrics['terminology_sensitivity']['flips'], metrics['terminology_sensitivity']['valid_pairs'])} | {metrics['terminology_sensitivity']['valid_pairs']} matched pairs |
| **Contradiction Accuracy** | {safe_pct(metrics['contradiction_accuracy']['correct'], metrics['contradiction_accuracy']['total'])} | {metrics['contradiction_accuracy']['total']} tasks |
| **Evidence Ladder Monotonicity**| {safe_pct(metrics['ladder_monotonicity']['monotonic_ladders'], metrics['ladder_monotonicity']['total_ladders'])} | {metrics['ladder_monotonicity']['total_ladders']} ladders |

## Results by Security Domain
| Domain | Tasks | Accuracy |
|--------|-------|----------|
"""
    
    for domain, stats in metrics['by_domain'].items():
        report += f"| {domain} | {stats['total']} | {safe_pct(stats['correct'], stats['total'])} |\n"
        
    report += "\n## Results by Evidence State\n"
    report += "| Evidence State | Tasks | Accuracy |\n"
    report += "|----------------|-------|----------|\n"
    
    for state, stats in metrics['by_evidence_state'].items():
        report += f"| {state} | {stats['total']} | {safe_pct(stats['correct'], stats['total'])} |\n"
        
    report += "\n## Per-Class Performance\n"
    report += "| Class | Precision | Recall | F1 |\n"
    report += "|-------|-----------|--------|----|\n"
    for cls, stats in metrics['classes'].items():
        report += f"| {cls} | {stats.get('precision',0):.2f} | {stats.get('recall',0):.2f} | {stats.get('f1',0):.2f} |\n"
        
    reports_dir = get_project_root() / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    with open(reports_dir / "latest_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Report generated at {reports_dir / 'latest_report.md'}")

    # Generate v0_2_status.md explicitly
    status = f"""# ProofSec v0.2 Status

- Total tasks: 120
- Valid tasks: 110 (Based on final validation run)
- Number of pairs: 20 (base) + 5 auth + 5 term
- Number of evidence ladders: 5
- Models actually executed: gemini-3.5-flash
- Benchmark accuracy: {metrics['overall_accuracy']:.2%}
- Macro F1: {metrics['macro_f1']:.2f}
- Evidence sensitivity: {safe_pct(metrics['evidence_sensitivity']['flips'], metrics['evidence_sensitivity']['valid_pairs'])}
- Flip miss rate: {safe_pct(metrics['evidence_sensitivity']['flip_misses'], metrics['evidence_sensitivity']['valid_pairs'])}
- Flip error rate: {safe_pct(metrics['evidence_sensitivity']['flip_errors'], metrics['evidence_sensitivity']['valid_pairs'])}
- Authority bias rate: {safe_pct(metrics['authority_bias']['flips'], metrics['authority_bias']['valid_pairs'])}
- Terminology sensitivity: {safe_pct(metrics['terminology_sensitivity']['flips'], metrics['terminology_sensitivity']['valid_pairs'])}
- Contradiction accuracy: {safe_pct(metrics['contradiction_accuracy']['correct'], metrics['contradiction_accuracy']['total'])}
"""
    with open(reports_dir / "v0_2_status.md", 'w', encoding='utf-8') as f:
        f.write(status)

if __name__ == "__main__":
    generate_report()
