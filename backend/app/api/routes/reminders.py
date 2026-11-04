from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import Reminder, Task
from app.schemas.productivity import ReminderCreate, ReminderResponse
from app.services.audit import record_audit_event

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.get("", response_model=list[ReminderResponse])
def list_reminders(database: DatabaseSession, user: CurrentUser) -> list[Reminder]:
    return list(database.scalars(select(Reminder).where(Reminder.user_id == user.id).order_by(Reminder.remind_at)))


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, database: DatabaseSession, user: CurrentUser) -> Reminder:
    if payload.task_id is not None and database.scalar(select(Task.id).where(Task.id == payload.task_id, Task.user_id == user.id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    reminder = Reminder(user_id=user.id, **payload.model_dump())
    database.add(reminder)
    record_audit_event(database, "reminder.created", user.id)
    database.commit()
    database.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: UUID, database: DatabaseSession, user: CurrentUser) -> Response:
    reminder = database.scalar(select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user.id))
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    database.delete(reminder)
    record_audit_event(database, "reminder.deleted", user.id, f"reminder={reminder_id}")
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
