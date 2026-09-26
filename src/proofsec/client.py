import os
from typing import Optional, List
from .schemas import CustomEvaluationRequest, EvaluationResponse
from .evaluator import CustomEvaluator
from .providers import get_provider

class ProofSec:
    """ProofSec SDK Client."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize the ProofSec client.
        
        Args:
            provider: The name of the provider to use (e.g., 'openai_compatible', 'kaggle', 'mock').
                      If not provided, reads from PROOFSEC_PROVIDER environment variable.
        """
        if provider:
            os.environ['PROOFSEC_PROVIDER'] = provider
        
        self.provider_name = os.getenv('PROOFSEC_PROVIDER', 'kaggle')
        self.provider = get_provider()
        self.evaluator = CustomEvaluator(provider=self.provider)

    def evaluate(
        self,
        scenario: str,
        evidence: Optional[List[str]] = None,
        context: Optional[str] = None,
        question: Optional[str] = None,
        save: bool = True
    ) -> EvaluationResponse:
        """
        Evaluate a security scenario.

        Args:
            scenario: The security scenario description.
            evidence: List of observed evidence strings.
            context: Optional additional context.
            question: Optional specific question.
            save: Whether to save the evaluation record locally.

        Returns:
            EvaluationResponse object.
        """
        request = CustomEvaluationRequest(
            scenario=scenario,
            evidence=evidence or [],
            context=context,
            question=question
        )
        
        return self.evaluator.evaluate(request, save=save)

    def revise(
        self,
        evaluation_id: str,
        evidence: List[str]
    ) -> EvaluationResponse:
        """
        Revise a previous evaluation by adding new evidence.
        
        Args:
            evaluation_id: ID of the previous evaluation.
            evidence: New evidence to add.
            
        Returns:
            EvaluationResponse object for the new revision.
        """
        import json
        from .evaluator import get_project_root, _sanitize_id
        
        safe_id = _sanitize_id(evaluation_id)
        file_path = get_project_root() / "custom_evaluations" / f"{safe_id}.json"
        
        if not file_path.exists():
            raise ValueError(f"Evaluation '{evaluation_id}' not found.")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        original_request = data.get("request", {})
        combined_evidence = original_request.get("evidence", []) + evidence
        
        request = CustomEvaluationRequest(
            scenario=original_request.get("scenario", ""),
            context=original_request.get("context"),
            question=original_request.get("question"),
            evidence=combined_evidence,
            previous_evaluation_id=safe_id
        )
        
        return self.evaluator.evaluate(request, save=True)
        
    def health(self):
        """Check provider health."""
        return self.provider.health_check()
