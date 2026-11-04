from typing import Any

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=1_000)


class AgentRunResponse(BaseModel):
    status: str
    summary: str
    tool: str | None
    result: dict[str, Any] | None
