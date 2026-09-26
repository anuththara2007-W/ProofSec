import os
from typing import Dict, Type, Optional
from . import ModelProvider
from .kaggle import KaggleProvider
from .openai_compatible import OpenAIProvider
from .mock import MockProvider

class ProviderManager:
    def __init__(self):
        self._providers: Dict[str, Type[ModelProvider]] = {
            "kaggle": KaggleProvider,
            "openai_compatible": OpenAIProvider,
            "mock": MockProvider
        }

    def register(self, name: str, provider_class: Type[ModelProvider]):
        self._providers[name] = provider_class

    def get(self, name: Optional[str] = None) -> ModelProvider:
        name = name or os.environ.get("PROOFSEC_PROVIDER", "kaggle").lower()
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}")
        return self._providers[name]()

    def list_providers(self) -> Dict[str, Type[ModelProvider]]:
        return self._providers

provider_manager = ProviderManager()

def get_provider(name: Optional[str] = None) -> ModelProvider:
    return provider_manager.get(name)
