"""
ProofSec — Evidence-grounded security reasoning evaluation platform.

Usage:
    from proofsec import ProofSec

    client = ProofSec(provider="openai_compatible")
    
    result = client.evaluate(
        scenario="An API returns user data at /users/{id}",
        evidence=["Sequential IDs", "HTTP 200 with data for /users/1002"]
    )
    print(result.classification)
"""

from .client import ProofSec
from .schemas import EvaluationResponse, CustomEvaluationRequest

__all__ = ["ProofSec", "EvaluationResponse", "CustomEvaluationRequest"]
