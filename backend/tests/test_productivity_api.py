from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


def test_authenticated_user_can_manage_tasks_and_conversations() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)

    def override_db() -> Generator[Session, None, None]:
        database = session_factory()
        try:
            yield database
        finally:
            database.close()

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            registration = client.post("/api/v1/auth/register", json={"email": "ada@example.com", "password": "correct-horse-battery"})
            assert registration.status_code == 201
            headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

            task = client.post("/api/v1/tasks", headers=headers, json={"title": "Review architecture", "priority": "high"})
            assert task.status_code == 201
            assert task.json()["status"] == "open"

            conversation = client.post("/api/v1/conversations", headers=headers, json={})
            assert conversation.status_code == 201
            message = client.post(f"/api/v1/conversations/{conversation.json()['id']}/messages", headers=headers, json={"content": "Plan my day"})
            assert message.status_code == 201
            assert message.json()["sequence"] == 1
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
