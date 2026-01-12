from app.core.config import settings

from .base import LLMProvider
from .claude_cli import ClaudeCLIProvider
from .ollama import OllamaProvider

LLM_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "claude": ClaudeCLIProvider,
}


def get_llm_provider(name: str | None = None) -> LLMProvider:
    provider_name = name or settings.llm_provider
    provider_class = LLM_PROVIDERS.get(provider_name)
    if provider_class is None:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return provider_class()
