from typing import TypeVar, cast

from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.llm = ChatOllama(
            model=model or settings.ollama_model,
            base_url=base_url or settings.ollama_host,
            temperature=0,
        )

    async def extract_structured(
        self,
        content: str,
        schema: type[T],
        prompt: str | None = None,
    ) -> T:
        structured_llm = self.llm.with_structured_output(schema)
        base_prompt = prompt or "Extract the data from this content."
        full_prompt = f"{base_prompt}\n\nContent:\n{content}"
        result = await structured_llm.ainvoke(full_prompt)
        return cast(T, result)

    async def generate(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)
        return str(response.content)
