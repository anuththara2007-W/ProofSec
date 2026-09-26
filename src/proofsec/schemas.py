from typing import Literal
from pydantic import BaseModel, Field

class SecurityAssessment(BaseModel):
    evidence_available: str = Field(description="What is directly observed?")
    evidence_missing: str = Field(description="What information is required before concluding an authorization vulnerability exists?")
    safe_verification_procedure: str = Field(description="Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment")
    classification: Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"] = Field(description="Must be exactly one of the three canonical labels")
    reasoning_confidence: int = Field(description="Confidence in classification (0-100)", ge=0, le=100)
