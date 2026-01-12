from typing import TypeVar

from pydantic import BaseModel

from .llm_providers import get_llm_provider

T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self, provider: str | None = None):
        self._provider = get_llm_provider(provider)

    async def extract_structured(
        self,
        content: str,
        schema: type[T],
        prompt: str | None = None,
    ) -> T:
        return await self._provider.extract_structured(content, schema, prompt)

    async def generate(self, prompt: str) -> str:
        return await self._provider.generate(prompt)
