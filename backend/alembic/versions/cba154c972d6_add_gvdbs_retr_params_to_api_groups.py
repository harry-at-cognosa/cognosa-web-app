"""add gvdbs_retr_params to api_groups

Revision ID: cba154c972d6
Revises: adf87cf4e03f
Create Date: 2026-01-24 05:22:59.315648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'cba154c972d6'
down_revision: Union[str, Sequence[str], None] = 'adf87cf4e03f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add the column as nullable first
    op.add_column(
        'api_groups',
        sa.Column('gvdbs_retr_params', sa.VARCHAR(), nullable=True)
    )
    
    # Step 2: Populate the column with value from api_settings
    connection = op.get_bind()
    
    # Get the value from api_settings
    result = connection.execute(
        text("SELECT value FROM api_settings WHERE name = 'gvdbs_def_retr_params'")
    ).fetchone()
    
    if result is None:
        raise ValueError(
            "Cannot find 'gvdbs_def_retr_params' in api_settings table. "
            "Please ensure this setting exists before running the migration."
        )
    
    default_value = result[0]
    
    # Update all existing rows with the value
    connection.execute(
        text("UPDATE api_groups SET gvdbs_retr_params = :value"),
        {"value": default_value}
    )
    
    # Step 3: Make the column non-nullable
    op.alter_column(
        'api_groups',
        'gvdbs_retr_params',
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the column
    op.drop_column('api_groups', 'gvdbs_retr_params')
