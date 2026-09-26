import json
from pathlib import Path
import sys

def get_project_root():
    return Path(__file__).parent.parent

def generate_report():
    root = get_project_root()
    comp_file = root / "results" / "metrics" / "model_comparison.json"
    
    with open(comp_file, 'r', encoding='utf-8') as f:
        comp = json.load(f)
        
    models_data = comp.get('models', [])
    if not models_data:
        return
        
    m = models_data[0] # Just use first for detailed breakdown if needed, or aggregate.
    
    report = f"""# ProofSec v0.2.1 Final Report

## Executive Summary
ProofSec v0.2 is frozen at 110 valid JSON tasks measuring Evidence-Grounded Security Reasoning.

## Research Question
"Does an AI model change its security judgment appropriately when the evidence changes?"

## Benchmark Design
- One-Fact Flips (40)
- Evidence Ladders (20)
- Contradiction (10)
- Authority Bias / Terminology (20)
- Baseline Tests (20)

## Dataset Composition
- Total tasks: 110
- Frozen Hash: {m.get('dataset_sha256', 'N/A')}

## Models Evaluated
"""
    for x in models_data:
        report += f"- {x['model']} ({x['task_count']} evaluations)\n"
        
    report += "\n## Overall Results\n"
    for x in models_data:
        report += f"**{x['model']}**\n- Accuracy: {x['accuracy']:.2%}\n- Macro F1: {x['macro_f1']:.2f}\n"

    report += "\n## Evidence-Grounded Results\n"
    for x in models_data:
        report += f"**{x['model']}**\n- Evidence Sensitivity: {x['evidence_sensitivity']:.2%}\n- Flip Miss Rate: {x['flip_miss_rate']:.2%}\n"
        report += f"- Authority Bias Rate: {x['authority_bias_rate']:.2%}\n- Terminology Sensitivity: {x['terminology_sensitivity_rate']:.2%}\n"
        report += f"- Contradiction Accuracy: {x['contradiction_accuracy']:.2%}\n- Ladder Monotonicity: {x['ladder_monotonicity']:.2%}\n"
        report += f"- Premature Vulnerability Rate (PVR): {x['premature_vulnerability_rate']:.2%}\n\n"

    report += """## Infrastructure Failures
- Encountered 401 Authentication Error (expired token) during main execution of Gemini.
- Runner upgraded to support `--resume` to recover safely.
- Token natively expired and prevented full 110 completion (stalled at 88/110 tasks).

## Limitations
Due to fatal Kaggle API auth expiry in this environment, evaluations were gracefully halted at 88 tasks. Missing 22 tasks.

## Reproducibility Information
See `docs/REPRODUCIBILITY.md`

## Conclusion
Infrastructure complete. Evaluation pipeline correctly metrics the PVR, Sensitivity, and Bias parameters.
"""
    with open(root / "results" / "reports" / "v0_2_final_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
        
    status = """# ProofSec v0.2.1 Status

## Benchmark
v0.2 Frozen.

## Dataset
110 valid tasks. SHA256 hashed and manifest created.

## Validation
Passed validation against duplicate, schema, and leakage tests.

## Experiments
Experiment runner fully supports fresh/resume and multi-model configuration.

## Models
gemini-3.5-flash

## Metrics
Implemented Evidence Sensitivity, Flip Error Rate, PVR, Authority Bias, Terminology Sensitivity.

## Statistics
Bootstrap Confidence Intervals script functional.

## Findings
Model showed strong resistance to Authority Bias but demonstrated measurable PVR.

## Failures
Encountered Kaggle 401 Auth exception on execution. 

## Limitations
Only 88 tasks fully evaluated due to infrastructure token limitations.

## Reproducibility
`docs/REPRODUCIBILITY.md` and `scripts/run_benchmark.py --resume` implemented.

## Repository State
Clean and tracked. Generated execution configs removed from root.

## Completion Status
BLOCKED (Infrastructure complete, Experiment incomplete due to API token expiry)
"""
    with open(root / "results" / "reports" / "v0_2_1_status.md", 'w', encoding='utf-8') as f:
        f.write(status)

if __name__ == "__main__":
    generate_report()
