from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    async def extract_structured(
        self,
        content: str,
        schema: type[T],
        prompt: str | None = None,
    ) -> T:
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
