from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.system import router as system_router
from app.api.routes.auth import router as auth_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.chat import router as chat_router
from app.api.routes.agent import router as agent_router
from app.api.routes.memory import router as memory_router
from app.api.routes.reminders import router as reminders_router
from app.api.routes.tasks import router as tasks_router
from app.core.config import get_settings
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

settings = get_settings()

app = FastAPI(
    title="JARVIS API",
    version="0.1.0",
    description="Secure service layer for the JARVIS personal assistant.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(tasks_router)
app.include_router(reminders_router)
