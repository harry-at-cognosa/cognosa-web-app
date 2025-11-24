"""add new gllms_type variants

Revision ID: 1f84f4203c8f
Revises: b2a6141d5fde
Create Date: 2025-11-24 15:08:43.710051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f84f4203c8f'
down_revision: Union[str, Sequence[str], None] = 'b2a6141d5fde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) create new enum type with added values
    op.execute(
        "CREATE TYPE gllms_type_enum_new AS ENUM ('dummy', 'ollama_local', 'ollama_remote', 'chatgpt', 'gemini', 'claude');"
    )
    # 2) alter column to use new enum type (casting via text)
    #    preserve NOT NULL / defaults are kept by ALTER COLUMN TYPE
    op.execute(
        "ALTER TABLE group_llms ALTER COLUMN gllms_type TYPE gllms_type_enum_new USING gllms_type::text::gllms_type_enum_new;"
    )
    # 3) drop old enum type and rename new to the original name
    op.execute("DROP TYPE IF EXISTS gllms_type_enum;")
    op.execute("ALTER TYPE gllms_type_enum_new RENAME TO gllms_type_enum;")


def downgrade() -> None:
    pass