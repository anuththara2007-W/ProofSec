"""
ProofSec — Evidence-grounded security reasoning evaluation platform.

Usage:
    from src.proofsec import evaluate

    result = evaluate(
        scenario="An API returns user data at /users/{id}",
        evidence=["Sequential IDs", "HTTP 200 with data for /users/1002"]
    )
"""
from src.proofsec.schemas import CustomEvaluationRequest, CustomEvaluationResult, CUSTOM_EVALUATION_VERSION
from src.proofsec.evaluator import CustomEvaluator
from src.proofsec.providers import get_provider


def evaluate(scenario: str, evidence: list = None, context: str = None, question: str = None, provider=None):
    """Evaluate a security scenario with the given evidence.

    Args:
        scenario: The security scenario description.
        evidence: List of observed evidence strings.
        context: Optional additional context.
        question: Optional specific question.
        provider: Optional ModelProvider instance. Defaults to env-configured provider.

    Returns:
        CustomEvaluationResult with classification, evidence_state, reasoning, etc.

    Raises:
        RuntimeError: On provider failure (auth, timeout, etc.)
        ValueError: On invalid input (oversized scenario, too many evidence items)
    """
    request = CustomEvaluationRequest(
        scenario=scenario,
        evidence=evidence or [],
        context=context,
        question=question
    )
    evaluator = CustomEvaluator(provider=provider)
    return evaluator.evaluate(request)
