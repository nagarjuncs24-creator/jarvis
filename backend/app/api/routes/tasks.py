from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import Task
from app.schemas.productivity import TaskCreate, TaskResponse, TaskUpdate
from app.services.audit import record_audit_event

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def owned_task(database: DatabaseSession, user_id: UUID, task_id: UUID) -> Task:
    task = database.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(database: DatabaseSession, user: CurrentUser) -> list[Task]:
    return list(database.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.status, Task.due_at)))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, database: DatabaseSession, user: CurrentUser) -> Task:
    task = Task(user_id=user.id, **payload.model_dump())
    database.add(task)
    record_audit_event(database, "task.created", user.id)
    database.commit()
    database.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, payload: TaskUpdate, database: DatabaseSession, user: CurrentUser) -> Task:
    task = owned_task(database, user.id, task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    if task.status == "completed" and task.completed_at is None:
        task.completed_at = datetime.now(UTC)
    elif task.status != "completed":
        task.completed_at = None
    record_audit_event(database, "task.updated", user.id, f"task={task.id}")
    database.commit()
    database.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, database: DatabaseSession, user: CurrentUser) -> Response:
    task = owned_task(database, user.id, task_id)
    database.delete(task)
    record_audit_event(database, "task.deleted", user.id, f"task={task_id}")
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
