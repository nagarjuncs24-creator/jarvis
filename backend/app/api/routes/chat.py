import asyncio
import json
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select

from app.ai.llm import ChatTurn, LLMConfigurationError, get_llm_provider
from app.ai.prompts import SYSTEM_PROMPT
from app.agents.orchestrator import agent_graph
from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import Conversation, Message, ToolExecution
from app.schemas.conversations import MessageCreate
from app.services.audit import record_audit_event

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def sse(event: str, data: dict[str, str]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def get_owned_conversation(database: DatabaseSession, user_id: UUID, conversation_id: UUID) -> Conversation:
    conversation = database.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id))
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


def tool_result_text(tool: str, result: dict) -> str:
    if tool == "calculator":
        return f"{result['expression']} = {result['result']:g}"
    if tool == "date_time":
        return f"The current UTC time is {result['utc']}."
    return "The approved tool completed."


@router.post("/{conversation_id}/stream")
async def stream_chat(conversation_id: UUID, payload: MessageCreate, database: DatabaseSession, user: CurrentUser) -> StreamingResponse:
    conversation = get_owned_conversation(database, user.id, conversation_id)
    agent_result = agent_graph.invoke({"instruction": payload.content, "planned_tool": None, "tool_input": {}, "tool_result": None, "status": "pending", "summary": ""})
    provider = None
    if agent_result["planned_tool"] is None:
        try:
            provider = get_llm_provider()
        except LLMConfigurationError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    next_sequence = database.scalar(select(func.coalesce(func.max(Message.sequence), 0) + 1).where(Message.conversation_id == conversation.id))
    database.add(Message(conversation_id=conversation.id, role="user", content=payload.content, sequence=next_sequence))
    if agent_result["planned_tool"] is not None:
        database.add(ToolExecution(user_id=user.id, tool_name=agent_result["planned_tool"], status=agent_result["status"], summary=agent_result["summary"]))
    database.commit()
    history = list(database.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.sequence.desc()).limit(30)))
    turns = [ChatTurn(role="system", content=SYSTEM_PROMPT)] + [ChatTurn(role=message.role, content=message.content) for message in reversed(history)]
    async def generate() -> AsyncIterator[str]:
        chunks: list[str] = []
        try:
            yield sse("status", {"state": "generating"})
            if agent_result["planned_tool"] is not None:
                if agent_result["status"] == "failed":
                    text = agent_result["summary"]
                else:
                    text = tool_result_text(agent_result["planned_tool"], agent_result["tool_result"])
                chunks.append(text)
                yield sse("tool", {"name": agent_result["planned_tool"]})
                yield sse("token", {"text": text})
            else:
                async for chunk in provider.stream_text(turns):
                    chunks.append(chunk)
                    yield sse("token", {"text": chunk})
            text = "".join(chunks).strip()
            if text:
                database.add(Message(conversation_id=conversation.id, role="assistant", content=text, sequence=next_sequence + 1))
                record_audit_event(database, "chat.completed", user.id, f"conversation={conversation.id}")
                database.commit()
            yield sse("done", {"state": "completed"})
        except Exception:
            database.rollback()
            yield sse("error", {"message": "The model response could not be completed. Please try again."})
        finally:
            await asyncio.sleep(0)

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
