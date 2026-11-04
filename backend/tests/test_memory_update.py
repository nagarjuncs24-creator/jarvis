from app.schemas.memory import MemoryUpdate


def test_memory_update_validates_content() -> None:
    assert MemoryUpdate(content="Use concise answers").content == "Use concise answers"
