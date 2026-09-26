import os
from typing import Optional, List
from .schemas import CustomEvaluationRequest, CustomEvaluationResult
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
        previous_evaluation_id: Optional[str] = None,
        save: bool = True
    ) -> CustomEvaluationResult:
        """
        Evaluate a security scenario.

        Args:
            scenario: The security scenario description.
            evidence: List of observed evidence strings.
            context: Optional additional context.
            question: Optional specific question.
            previous_evaluation_id: ID of the previous evaluation in a revision chain.
            save: Whether to save the evaluation record locally.

        Returns:
            CustomEvaluationResult object.
        """
        request = CustomEvaluationRequest(
            scenario=scenario,
            evidence=evidence or [],
            context=context,
            question=question,
            previous_evaluation_id=previous_evaluation_id
        )
        
        result = self.evaluator.evaluate(request)
        
        if save:
            eval_id, _ = self.evaluator.save_evaluation(request, result)
            # Inject evaluation_id so the caller has it (we'll modify CustomEvaluationResult schema slightly to allow it, or just return a tuple/wrapper if needed. But for SDK, a clean wrapper is best).
            
            # For now, let's just attach it dynamically or return a wrapper if we don't modify schema.
            # Actually, user phase 9 says: "A successful response should contain structured fields similar to: evaluation_id, version, classification, evidence_state, confidence...".
            # I will modify the schema next to include these fields directly.
            
        return result
