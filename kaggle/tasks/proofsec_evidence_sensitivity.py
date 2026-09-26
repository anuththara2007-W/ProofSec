import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pydantic import BaseModel, Field
from typing import Literal
import kaggle_benchmarks as kbench
from kaggle.adapters.proofsec_adapter import load_task, build_prompt

class SecurityAssessment(BaseModel):
    classification: Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"] = Field(description="Must be exactly one of the three canonical labels")
    evidence_state: Literal["WEAK", "PARTIAL", "DECISIVE", "CONTRADICTORY", "NEGATIVE", "UNKNOWN"] = Field(description="Evidence state classification")
    supporting_evidence: str = Field(description="Supporting evidence identified")
    missing_evidence: str = Field(description="Missing evidence required")
    safe_verification: str = Field(description="Safe verification procedure")
    impact: str = Field(description="Potential impact")

@kbench.task("proofsec-evidence-sensitivity")
def evidence_sensitivity_task(llm) -> None:
    task_data = load_task("task-001-idor-bola-evidence-test")
    prompt = build_prompt(task_data)
    
    response = llm.prompt(prompt, schema=SecurityAssessment)
    
    print(f"Classification: {response.classification}")
