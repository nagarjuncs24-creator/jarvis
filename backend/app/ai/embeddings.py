from openai import OpenAI

from app.core.config import get_settings


class EmbeddingConfigurationError(RuntimeError):
    pass


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    if settings.llm_provider.lower() != "openai" or not settings.openai_api_key or not settings.embedding_model:
        raise EmbeddingConfigurationError("OPENAI_API_KEY and EMBEDDING_MODEL must be configured for semantic memory")
    response = OpenAI(api_key=settings.openai_api_key).embeddings.create(model=settings.embedding_model, input=text)
    return response.data[0].embedding
