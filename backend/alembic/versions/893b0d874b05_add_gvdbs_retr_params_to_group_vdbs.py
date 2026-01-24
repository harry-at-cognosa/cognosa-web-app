"""add gvdbs_retr_params to group_vdbs

Revision ID: 893b0d874b05
Revises: cba154c972d6
Create Date: 2026-01-24 05:36:13.807523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '893b0d874b05'
down_revision: Union[str, Sequence[str], None] = 'cba154c972d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add the column as nullable first
    op.add_column(
        'group_vdbs',
        sa.Column('gvdbs_retr_params', sa.VARCHAR(), nullable=True)
    )
    
    # Step 2: Populate the column with values from api_groups based on group_id
    connection = op.get_bind()
    
    # Update group_vdbs with values from api_groups
    connection.execute(
        text("""
            UPDATE group_vdbs 
            SET gvdbs_retr_params = api_groups.gvdbs_retr_params
            FROM api_groups
            WHERE group_vdbs.group_id = api_groups.group_id
        """)
    )
    
    # Step 3: Check if any rows still have NULL values (orphaned records)
    null_count = connection.execute(
        text("SELECT COUNT(*) FROM group_vdbs WHERE gvdbs_retr_params IS NULL")
    ).scalar()
    
    if null_count:
        raise ValueError(
            f"Found {null_count} rows in group_vdbs that don't have matching group_id "
            "in api_groups table. Please fix data integrity issues before running this migration."
        )
    
    # Step 4: Make the column non-nullable
    op.alter_column(
        'group_vdbs',
        'gvdbs_retr_params',
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the column
    op.drop_column('group_vdbs', 'gvdbs_retr_params')
