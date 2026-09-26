from typing import Type, Dict, Any
from pydantic import BaseModel
from . import ModelProvider, ProviderResponse, ProviderStatus, HealthStatus

class MockProvider(ModelProvider):
    def __init__(self, mock_response=None, mock_status=ProviderStatus.AVAILABLE):
        self.mock_response = mock_response
        self.mock_status = mock_status
        if self.mock_response is None and self.mock_status == ProviderStatus.AVAILABLE:
            from proofsec.schemas import CustomEvaluationResult
            self.mock_response = CustomEvaluationResult(
                summary="Mock response summary",
                classification="Insufficient Evidence",
                evidence_state="PARTIAL",
                confidence=85,
                supporting_evidence=["Simulated mock evidence"],
                missing_evidence=[],
                contradicting_evidence=[],
                safe_verification=["Simulated verification"],
                impact="TEST FIXTURE",
                reasoning="Mock response"
            )
        
    @property
    def provider_name(self) -> str:
        return "mock"
        
    @property
    def model_name(self) -> str:
        return "mock-model"
        
    @property
    def model_version(self) -> str:
        return "1.0"
        
    def evaluate_request(self, prompt: str, schema: Type[BaseModel]) -> ProviderResponse:
        return ProviderResponse(status=self.mock_status, result=self.mock_response)
        
    def health_check(self) -> HealthStatus:
        return HealthStatus(provider=self.provider_name, model=self.model_name, status=self.mock_status)

    def authenticate(self) -> bool:
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "authentication": "none",
            "benchmark_integration": False
        }
