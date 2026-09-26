from typing import Literal, List, Optional
from pydantic import BaseModel, Field

class SecurityAssessment(BaseModel):
    evidence_available: str = Field(description="What is directly observed?")
    evidence_missing: str = Field(description="What information is required before concluding an authorization vulnerability exists?")
    safe_verification_procedure: str = Field(description="Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment")
    classification: Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"] = Field(description="Must be exactly one of the three canonical labels")
    reasoning_confidence: int = Field(description="Confidence in classification (0-100)", ge=0, le=100)

class CustomEvaluationRequest(BaseModel):
    scenario: str = Field(description="The security scenario description")
    evidence: List[str] = Field(default_factory=list, description="Observed evidence")
    context: Optional[str] = Field(default=None, description="Optional additional context")
    question: Optional[str] = Field(default=None, description="Specific user question")

class CustomEvaluationResult(BaseModel):
    classification: Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"]
    evidence_state: Literal["WEAK", "PARTIAL", "DECISIVE", "CONTRADICTORY", "NEGATIVE", "UNKNOWN"]
    supporting_evidence: List[str]
    missing_evidence: List[str]
    safe_verification: List[str]
    impact: str
    reasoning: str
