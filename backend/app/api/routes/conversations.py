from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import Conversation, Message
from app.schemas.conversations import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.services.audit import record_audit_event

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def owned_conversation(database: DatabaseSession, user_id: UUID, conversation_id: UUID) -> Conversation:
    conversation = database.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id))
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(database: DatabaseSession, user: CurrentUser) -> list[Conversation]:
    return list(database.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())))


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, database: DatabaseSession, user: CurrentUser) -> Conversation:
    conversation = Conversation(user_id=user.id, title=payload.title)
    database.add(conversation)
    record_audit_event(database, "conversation.created", user.id)
    database.commit()
    database.refresh(conversation)
    return conversation


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(conversation_id: UUID, database: DatabaseSession, user: CurrentUser) -> list[Message]:
    owned_conversation(database, user.id, conversation_id)
    return list(database.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.sequence)))


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_user_message(conversation_id: UUID, payload: MessageCreate, database: DatabaseSession, user: CurrentUser) -> Message:
    conversation = owned_conversation(database, user.id, conversation_id)
    next_sequence = database.scalar(select(func.coalesce(func.max(Message.sequence), 0) + 1).where(Message.conversation_id == conversation.id))
    message = Message(conversation_id=conversation.id, role="user", content=payload.content, sequence=next_sequence)
    database.add(message)
    conversation.title = conversation.title if conversation.title != "New conversation" else payload.content[:80]
    record_audit_event(database, "message.created", user.id, f"conversation={conversation.id}")
    database.commit()
    database.refresh(message)
    return message
