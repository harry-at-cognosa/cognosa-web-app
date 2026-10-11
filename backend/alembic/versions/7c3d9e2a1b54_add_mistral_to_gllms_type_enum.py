"""add mistral to gllms_type_enum

Revision ID: 7c3d9e2a1b54
Revises: 22cb85c671f5
Create Date: 2026-10-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c3d9e2a1b54'
down_revision: Union[str, Sequence[str], None] = '22cb85c671f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'mistral' to gllms_type_enum."""
    op.execute(
        "CREATE TYPE gllms_type_enum_new AS ENUM ('dummy', 'ollama_local', 'ollama_remote', 'chatgpt', 'gemini', 'claude', 'qwen', 'mistral');"
    )
    op.execute(
        "ALTER TABLE group_llms ALTER COLUMN gllms_type TYPE gllms_type_enum_new USING gllms_type::text::gllms_type_enum_new;"
    )
    op.execute("DROP TYPE IF EXISTS gllms_type_enum;")
    op.execute("ALTER TYPE gllms_type_enum_new RENAME TO gllms_type_enum;")


def downgrade() -> None:
    pass
