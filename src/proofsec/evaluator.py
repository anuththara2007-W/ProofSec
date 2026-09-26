import json
import time
from typing import Optional
from pathlib import Path

from src.proofsec.schemas import CustomEvaluationRequest, CustomEvaluationResult

from src.proofsec.providers import ModelProvider, ProviderStatus, get_provider

def get_project_root():
    return Path(__file__).parent.parent.parent

class CustomEvaluator:
    def __init__(self, provider: Optional[ModelProvider] = None):
        self.provider = provider or get_provider()

    def _build_prompt(self, request: CustomEvaluationRequest) -> str:
        prompt = "SYSTEM/DEVELOPER EVALUATION INSTRUCTIONS\n"
        prompt += "You are an expert security code reviewer focused on strict evidence-based reasoning.\n"
        prompt += "Evaluate whether the evidence strictly proves the existence of a vulnerability. Do not assume vulnerabilities based on weak indicators.\n"
        prompt += "Assign an evidence state (WEAK, PARTIAL, DECISIVE, CONTRADICTORY, NEGATIVE).\n"
        prompt += "Provide a safe verification procedure if evidence is missing.\n"
        prompt += "Use the required structured output schema.\n\n"
        
        prompt += "USER-PROVIDED SCENARIO\n"
        prompt += f"{request.scenario}\n\n"
        
        if request.evidence:
            prompt += "USER-PROVIDED EVIDENCE\n"
            for idx, ev in enumerate(request.evidence, 1):
                prompt += f"{idx}. {ev}\n"
            prompt += "\n"
            
        if request.context:
            prompt += f"USER-PROVIDED CONTEXT\n{request.context}\n\n"
            
        if request.question:
            prompt += f"USER-PROVIDED QUESTION\n{request.question}\n\n"
            
        return prompt

    def evaluate(self, request: CustomEvaluationRequest) -> CustomEvaluationResult:
        prompt = self._build_prompt(request)
        
        response = self.provider.evaluate_request(prompt, schema=CustomEvaluationResult)
        
        if response.status != ProviderStatus.AVAILABLE:
            raise RuntimeError(f"Evaluation failed: {response.status} ({response.error_message})")
            
        return response.result

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
