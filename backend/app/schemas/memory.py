from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MemoryCreate(BaseModel):
    content: str = Field(min_length=2, max_length=10_000)
    kind: str = Field(default="fact", pattern="^(fact|preference|project|instruction)$")
    consent: bool


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: str
    content: str
    created_at: datetime
