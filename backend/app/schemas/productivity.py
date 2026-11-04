from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=10_000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=10_000)
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    status: str | None = Field(default=None, pattern="^(open|completed|cancelled)$")
    due_at: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    remind_at: datetime
    task_id: UUID | None = None


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    task_id: UUID | None
    remind_at: datetime
    status: str
    created_at: datetime
