import asyncio
import json
from typing import TypeVar

from pydantic import BaseModel

from .base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class ClaudeCLIProvider(LLMProvider):
    async def _run_claude(self, prompt: str, output_format: str = "text") -> str:
        proc = await asyncio.create_subprocess_exec(
            "claude",
            "-p",
            "--output-format",
            output_format,
            "--allowedTools",
            "",
            "--dangerously-skip-permissions",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(prompt.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {stderr.decode()}")
        return stdout.decode()

    async def extract_structured(
        self,
        content: str,
        schema: type[T],
        prompt: str | None = None,
    ) -> T:
        schema_json = schema.model_json_schema()
        full_prompt = (
            f"{prompt or 'Extract data from content.'}\n\n"
            f"Content:\n{content}\n\n"
            f"Respond ONLY with valid JSON matching this schema (no markdown, no explanation):\n"
            f"{json.dumps(schema_json, indent=2)}"
        )

        output = await self._run_claude(full_prompt, "json")
        data = json.loads(output)
        return schema.model_validate(data["result"])

    async def generate(self, prompt: str) -> str:
        return await self._run_claude(prompt, "text")
