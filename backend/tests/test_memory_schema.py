import pytest

from pydantic import ValidationError

from app.schemas.memory import MemoryCreate


def test_memory_requires_explicit_consent_field() -> None:
    with pytest.raises(ValidationError):
        MemoryCreate(content="I prefer concise answers")
