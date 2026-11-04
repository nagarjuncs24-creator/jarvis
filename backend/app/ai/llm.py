from collections.abc import AsyncIterator
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import Settings, get_settings


class LLMConfigurationError(RuntimeError):
    """Raised when an LLM provider is selected without valid server-side configuration."""


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class OpenAIResponsesProvider:
    """Backend-only adapter around the Responses API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def stream_text(self, turns: list[ChatTurn]) -> AsyncIterator[str]:
        stream = await self._client.responses.create(
            model=self._model,
            input=[{"role": turn.role, "content": turn.content} for turn in turns],
            stream=True,
        )
        async for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta


def get_llm_provider(settings: Settings | None = None) -> OpenAIResponsesProvider:
    configured = settings or get_settings()
    if configured.llm_provider.lower() != "openai":
        raise LLMConfigurationError("No supported LLM provider is configured")
    if not configured.openai_api_key or not configured.openai_model:
        raise LLMConfigurationError("OPENAI_API_KEY and OPENAI_MODEL must be configured before streaming chat")
    return OpenAIResponsesProvider(configured.openai_api_key, configured.openai_model)
