"""productivity and chat

Revision ID: 0002_productivity_and_chat
Revises: 0001_identity_foundation
Create Date: 2026-11-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_productivity_and_chat"
down_revision = "0001_identity_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = sa.Uuid()
    op.create_table("conversations", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_table("messages", sa.Column("id", uuid, primary_key=True), sa.Column("conversation_id", uuid, nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text())), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"), sa.UniqueConstraint("conversation_id", "sequence", name="uq_messages_conversation_sequence"))
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_table("tasks", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, nullable=False), sa.Column("title", sa.String(250), nullable=False), sa.Column("description", sa.Text()), sa.Column("status", sa.String(20), nullable=False, server_default="open"), sa.Column("priority", sa.String(20), nullable=False, server_default="medium"), sa.Column("due_at", sa.DateTime(timezone=True)), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"]); op.create_index("ix_tasks_status", "tasks", ["status"]); op.create_index("ix_tasks_due_at", "tasks", ["due_at"])
    op.create_table("reminders", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, nullable=False), sa.Column("task_id", uuid), sa.Column("title", sa.String(250), nullable=False), sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"))
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"]); op.create_index("ix_reminders_task_id", "reminders", ["task_id"]); op.create_index("ix_reminders_remind_at", "reminders", ["remind_at"]); op.create_index("ix_reminders_status", "reminders", ["status"])


def downgrade() -> None:
    op.drop_table("reminders"); op.drop_table("tasks"); op.drop_table("messages"); op.drop_table("conversations")
