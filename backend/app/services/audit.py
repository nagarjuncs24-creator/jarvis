from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit_event(database: Session, event_type: str, user_id: UUID | None = None, detail: str | None = None) -> None:
    """Queue an audit record in the current database transaction."""
    database.add(AuditLog(user_id=user_id, event_type=event_type, detail=detail))
