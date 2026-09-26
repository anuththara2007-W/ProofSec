from typing import Literal, List, Optional
from pydantic import BaseModel, Field

# Research benchmark version: v0.2 (frozen, do not change)
# Custom evaluation API version (independent of benchmark version)
CUSTOM_EVALUATION_VERSION = "1.0"

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
    previous_evaluation_id: Optional[str] = Field(default=None, description="ID of the previous evaluation in a revision chain")
    expected_classification: Optional[str] = Field(default=None, description="User provided ground truth classification")
    expected_evidence_state: Optional[str] = Field(default=None, description="User provided ground truth evidence state")
    expected_decisive_fact: Optional[str] = Field(default=None, description="User provided ground truth decisive fact")

class CustomEvaluationResult(BaseModel):
    summary: str = Field(description="A concise 1-2 sentence summary of the evaluation.")
    classification: Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"]
    evidence_state: Literal["WEAK", "PARTIAL", "DECISIVE", "CONTRADICTORY", "NEGATIVE", "UNKNOWN"]
    confidence: Optional[int] = Field(default=None, description="Confidence in classification (0-100). Leave null if unable to determine.", ge=0, le=100)
    supporting_evidence: List[str]
    missing_evidence: List[str]
    contradicting_evidence: List[str] = Field(default_factory=list, description="Evidence that contradicts the primary classification.")
    safe_verification: List[str]
    impact: str
    reasoning: str

class EvaluationResponse(BaseModel):
    """The complete response returned by the API and SDK."""
    evaluation_id: str
    version: str
    classification: str
    evidence_state: str
    confidence: Optional[int]
    confidence_status: str
    summary: str
    supporting_evidence: List[str]
    missing_evidence: List[str]
    contradicting_evidence: List[str]
    safe_verification: List[str]
    impact: str
    reasoning: str
    provider: str
    model: str
    created_at: str
    previous_evaluation_id: Optional[str]

class CustomEvaluationRecord(BaseModel):
    request: CustomEvaluationRequest
    response: EvaluationResponse


