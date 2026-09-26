from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
from abc import ABC, abstractmethod
from enum import Enum

class ProviderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    PARSER_FAILURE = "PARSER_FAILURE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class ProviderResponse(BaseModel):
    status: ProviderStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None

class HealthStatus(BaseModel):
    provider: str
    model: str
    status: ProviderStatus

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
        
    @abstractmethod
    def authenticate(self) -> bool:
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        pass

from .manager import ProviderManager, get_provider, provider_manager
