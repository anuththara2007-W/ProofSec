import os
from typing import Type, Dict, Any
from pydantic import BaseModel
from . import ModelProvider, ProviderResponse, ProviderStatus, HealthStatus

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

    def authenticate(self) -> bool:
        return bool(self.api_key)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "authentication": "API key" if self.authenticate() else "missing",
            "benchmark_integration": False
        }
