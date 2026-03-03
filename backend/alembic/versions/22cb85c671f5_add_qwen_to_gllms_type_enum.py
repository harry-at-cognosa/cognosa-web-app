"""add qwen to gllms_type_enum

Revision ID: 22cb85c671f5
Revises: 445f136c55f3
Create Date: 2026-03-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22cb85c671f5'
down_revision: Union[str, Sequence[str], None] = '445f136c55f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'qwen' to gllms_type_enum."""
    op.execute(
        "CREATE TYPE gllms_type_enum_new AS ENUM ('dummy', 'ollama_local', 'ollama_remote', 'chatgpt', 'gemini', 'claude', 'qwen');"
    )
    op.execute(
        "ALTER TABLE group_llms ALTER COLUMN gllms_type TYPE gllms_type_enum_new USING gllms_type::text::gllms_type_enum_new;"
    )
    op.execute("DROP TYPE IF EXISTS gllms_type_enum;")
    op.execute("ALTER TYPE gllms_type_enum_new RENAME TO gllms_type_enum;")


def downgrade() -> None:
    pass
