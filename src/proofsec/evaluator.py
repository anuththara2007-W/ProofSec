import json
import time
from typing import Optional
from pathlib import Path

from src.proofsec.schemas import CustomEvaluationRequest, CustomEvaluationResult

def get_project_root():
    return Path(__file__).parent.parent.parent

class CustomEvaluator:
    def __init__(self, llm=None):
        self.llm = llm

    def _build_prompt(self, request: CustomEvaluationRequest) -> str:
        prompt = "You are an expert security code reviewer focused on strict evidence-based reasoning.\n\n"
        prompt += f"SCENARIO:\n{request.scenario}\n\n"
        
        if request.evidence:
            prompt += "EVIDENCE:\n"
            for idx, ev in enumerate(request.evidence, 1):
                prompt += f"{idx}. {ev}\n"
            prompt += "\n"
            
        if request.context:
            prompt += f"CONTEXT:\n{request.context}\n\n"
            
        if request.question:
            prompt += f"QUESTION:\n{request.question}\n\n"
            
        prompt += """INSTRUCTIONS:
Evaluate whether the evidence strictly proves the existence of a vulnerability. Do not assume vulnerabilities based on weak indicators.
Assign an evidence state (WEAK, PARTIAL, DECISIVE, CONTRADICTORY, NEGATIVE).
Provide a safe verification procedure if evidence is missing.
Use the required structured output schema.
"""
        return prompt

    def evaluate(self, request: CustomEvaluationRequest) -> CustomEvaluationResult:
        if not self.llm:
            try:
                import kaggle_benchmarks as kbench
                self.llm = kbench.llm
            except ImportError:
                raise RuntimeError("Provider unavailable: kaggle_benchmarks missing")
                
        prompt = self._build_prompt(request)
        
        try:
            # We use CustomEvaluationResult as the structured output schema
            response = self.llm.prompt(prompt, schema=CustomEvaluationResult)
            return response
        except Exception as e:
            if "401" in str(e) or "AuthenticationError" in str(e):
                raise RuntimeError("Provider authentication failed (HTTP 401).")
            raise RuntimeError(f"Evaluation failed due to infrastructure error: {e}")

    def save_evaluation(self, request: CustomEvaluationRequest, result: CustomEvaluationResult):
        product_dir = get_project_root() / "custom_evaluations"
        product_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = int(time.time())
        file_path = product_dir / f"eval_{timestamp}.json"
        
        data = {
            "timestamp": timestamp,
            "request": request.model_dump(),
            "result": result.model_dump()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        return file_path
