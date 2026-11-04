from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import Memory
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.audit import record_audit_event

router = APIRouter(prefix="/api/v1/memories", tags=["memory"])


@router.get("", response_model=list[MemoryResponse])
def list_memories(database: DatabaseSession, user: CurrentUser) -> list[Memory]:
    return list(database.scalars(select(Memory).where(Memory.user_id == user.id).order_by(Memory.updated_at.desc())))


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(payload: MemoryCreate, database: DatabaseSession, user: CurrentUser) -> Memory:
    if not payload.consent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Explicit consent is required to save memory")
    duplicate = database.scalar(select(Memory).where(Memory.user_id == user.id, Memory.content == payload.content))
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This memory is already saved")
    memory = Memory(user_id=user.id, content=payload.content, kind=payload.kind)
    database.add(memory)
    record_audit_event(database, "memory.created", user.id)
    database.commit()
    database.refresh(memory)
    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: UUID, database: DatabaseSession, user: CurrentUser) -> Response:
    memory = database.scalar(select(Memory).where(Memory.id == memory_id, Memory.user_id == user.id))
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    database.delete(memory)
    record_audit_event(database, "memory.deleted", user.id, f"memory={memory_id}")
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
