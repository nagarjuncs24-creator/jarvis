"""tool execution logs

Revision ID: 0004_tool_executions
Revises: 0003_memories
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_tool_executions"
down_revision = "0003_memories"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("tool_executions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("tool_name", sa.String(80)), sa.Column("status", sa.String(30), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_tool_executions_user_id", "tool_executions", ["user_id"])
    op.create_index("ix_tool_executions_status", "tool_executions", ["status"])

def downgrade() -> None:
    op.drop_table("tool_executions")
