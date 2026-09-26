from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
import os
import json

class ProviderStatus:
    AVAILABLE = "AVAILABLE"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PARSER_FAILURE = "PARSER_FAILURE"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class ProviderResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None

class HealthStatus(BaseModel):
    provider: str
    model: str
    status: str

class ModelProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def model_version(self) -> str:
        pass
        
    @abstractmethod
    def evaluate_request(self, prompt: str, schema: Type[BaseModel]) -> ProviderResponse:
        pass
        
    @abstractmethod
    def health_check(self) -> HealthStatus:
        pass

class KaggleProvider(ModelProvider):
    def __init__(self, model: str = None):
        self._model_name = model or os.environ.get("PROOFSEC_MODEL", "gemini-3.5-flash")
        try:
            import kaggle_benchmarks as kbench
            self.llm = kbench.llm
            self.is_configured = True
        except ImportError:
            self.llm = None
            self.is_configured = False

    @property
    def provider_name(self) -> str:
        return "kaggle"
        
    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def model_version(self) -> str:
        return "latest"
        
    def evaluate_request(self, prompt: str, schema: Type[BaseModel]) -> ProviderResponse:
        if not self.is_configured:
            return ProviderResponse(status=ProviderStatus.CONFIGURATION_ERROR, error_message="kaggle_benchmarks not found")
            
        try:
            res = self.llm.prompt(prompt, schema=schema)
            return ProviderResponse(status=ProviderStatus.AVAILABLE, result=res)
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "AuthenticationError" in err_str:
                return ProviderResponse(status=ProviderStatus.AUTHENTICATION_ERROR, error_message=err_str)
            if "Timeout" in err_str:
                return ProviderResponse(status=ProviderStatus.TIMEOUT, error_message=err_str)
            if "RateLimit" in err_str or "429" in err_str:
                return ProviderResponse(status=ProviderStatus.RATE_LIMIT, error_message=err_str)
            if "ValidationError" in err_str or "Unsupported type" in err_str:
                return ProviderResponse(status=ProviderStatus.PARSER_FAILURE, error_message=err_str)
            return ProviderResponse(status=ProviderStatus.UNKNOWN_ERROR, error_message=err_str)
            
    def health_check(self) -> HealthStatus:
        if not self.is_configured:
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.CONFIGURATION_ERROR)
        try:
            # lightweight call to see if auth is valid
            self.llm.prompt("test", schema=None)
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.AVAILABLE)
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "AuthenticationError" in err_str:
                return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.AUTHENTICATION_ERROR)
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.UNKNOWN_ERROR)

class OpenAIProvider(ModelProvider):
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self._model_name = model or os.environ.get("PROOFSEC_MODEL", "gpt-4o")
        self.api_key = api_key or os.environ.get("PROOFSEC_API_KEY")
        self.base_url = base_url or os.environ.get("PROOFSEC_BASE_URL", "https://api.openai.com/v1")
        
    @property
    def provider_name(self) -> str:
        return "openai_compatible"
        
    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def model_version(self) -> str:
        return "latest"
        
    def evaluate_request(self, prompt: str, schema: Type[BaseModel]) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(status=ProviderStatus.CONFIGURATION_ERROR, error_message="Missing PROOFSEC_API_KEY")
            
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            # Use beta parse for structured output if schema is provided
            completion = client.beta.chat.completions.parse(
                model=self._model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format=schema
            )
            return ProviderResponse(status=ProviderStatus.AVAILABLE, result=completion.choices[0].message.parsed)
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "AuthenticationError" in err_str:
                return ProviderResponse(status=ProviderStatus.AUTHENTICATION_ERROR, error_message=err_str)
            if "RateLimit" in err_str or "429" in err_str:
                return ProviderResponse(status=ProviderStatus.RATE_LIMIT, error_message=err_str)
            if "Timeout" in err_str:
                return ProviderResponse(status=ProviderStatus.TIMEOUT, error_message=err_str)
            return ProviderResponse(status=ProviderStatus.UNKNOWN_ERROR, error_message=err_str)
            
    def health_check(self) -> HealthStatus:
        if not self.api_key:
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.CONFIGURATION_ERROR)
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            client.models.list()
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.AVAILABLE)
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "AuthenticationError" in err_str:
                return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.AUTHENTICATION_ERROR)
            return HealthStatus(provider=self.provider_name, model=self.model_name, status=ProviderStatus.UNKNOWN_ERROR)

class MockProvider(ModelProvider):
    def __init__(self, mock_response=None, mock_status=ProviderStatus.AVAILABLE):
        self.mock_response = mock_response
        self.mock_status = mock_status
        
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

def get_provider() -> ModelProvider:
    provider_name = os.environ.get("PROOFSEC_PROVIDER", "kaggle").lower()
    if provider_name == "openai_compatible":
        return OpenAIProvider()
    if provider_name == "mock":
        from proofsec.schemas import CustomEvaluationResult
        return MockProvider(
            mock_response=CustomEvaluationResult(
                summary="Mock response summary",
                classification="Insufficient Evidence",
                evidence_state="PARTIAL",
                confidence=None,
                supporting_evidence=[],
                missing_evidence=[],
                contradicting_evidence=[],
                safe_verification=[],
                impact="TEST FIXTURE",
                reasoning="Mock response"
            )
        )
    return KaggleProvider()
