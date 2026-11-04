import pytest

from app.ai.llm import LLMConfigurationError, get_llm_provider
from app.core.config import Settings


def test_missing_provider_configuration_is_rejected() -> None:
    with pytest.raises(LLMConfigurationError):
        get_llm_provider(Settings(llm_provider=""))


def test_openai_provider_requires_server_side_credentials() -> None:
    with pytest.raises(LLMConfigurationError):
        get_llm_provider(Settings(llm_provider="openai", openai_api_key="", openai_model=""))
