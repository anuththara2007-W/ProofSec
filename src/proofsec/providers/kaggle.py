import os
from typing import Type, Dict, Any
from pydantic import BaseModel
from . import ModelProvider, ProviderResponse, ProviderStatus, HealthStatus

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

    def authenticate(self) -> bool:
        """Kaggle uses its own ~/.kaggle/kaggle.json authentication"""
        kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
        return os.path.exists(kaggle_json)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "authentication": "authenticated" if self.authenticate() else "none",
            "benchmark_integration": True
        }
