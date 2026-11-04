"""long term memories

Revision ID: 0003_memories
Revises: 0002_productivity_and_chat
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_memories"
down_revision = "0002_productivity_and_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("memories", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("kind", sa.String(30), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("vector_id", sa.String(36), unique=True), sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_memories_user_id", "memories", ["user_id"])


def downgrade() -> None:
    op.drop_table("memories")
