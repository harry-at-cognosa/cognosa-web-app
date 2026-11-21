"""add chat (conversation mode): tables, group switch, collection chat settings

Revision ID: 3f8a1c5d9e27
Revises: 7c3d9e2a1b54
Create Date: 2026-11-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8a1c5d9e27'
down_revision: Union[str, Sequence[str], None] = '7c3d9e2a1b54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Additive only: two new tables, three new columns, one settings row."""
    op.create_table(
        'chat_conversations',
        sa.Column('conv_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.VARCHAR(), server_default='', nullable=False),
        sa.Column('gvdbs_id', sa.Integer(), nullable=False),
        sa.Column('filters_json', sa.Text(), nullable=True),
        sa.Column('gllms_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['api_groups.group_id'], name='fk_chat_conversations_group_id'),
        sa.PrimaryKeyConstraint('conv_id'),
    )
    op.create_index(
        'ix_chat_conversations_user_id_updated_at', 'chat_conversations', ['user_id', 'updated_at'], unique=False)

    op.create_table(
        'chat_messages',
        sa.Column('msg_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conv_id', sa.Integer(), nullable=False),
        sa.Column('seqn', sa.Integer(), nullable=False),
        sa.Column('role', sa.VARCHAR(length=16), nullable=False),
        sa.Column('content', sa.Text(), server_default='', nullable=False),
        sa.Column('status', sa.VARCHAR(length=16), server_default='complete', nullable=False),
        sa.Column('gllms_id', sa.Integer(), nullable=True),
        sa.Column('retrieval_query', sa.Text(), nullable=True),
        sa.Column('tokens_in', sa.Integer(), nullable=True),
        sa.Column('tokens_out', sa.Integer(), nullable=True),
        sa.Column('seconds', sa.FLOAT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['conv_id'], ['chat_conversations.conv_id'], name='fk_chat_messages_conv_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('msg_id'),
        sa.UniqueConstraint('conv_id', 'seqn', name='uq_chat_messages_conv_id_seqn'),
    )

    op.add_column('api_groups', sa.Column('chat_enabled', sa.Boolean(), server_default=sa.text("'FALSE'"), nullable=False))
    op.add_column('api_groups', sa.Column('chat_rewrite_gllms_id', sa.Integer(), nullable=True))
    op.add_column('group_vdbs', sa.Column('gvdbs_chat_cfg', sa.VARCHAR(), server_default=sa.text("'{}'"), nullable=False))

    # Settings row for existing databases (new ones get it from .init_sql_data).
    op.execute(
        "INSERT INTO api_settings (name, value) "
        "SELECT 'chat_history_turns', '6' "
        "WHERE NOT EXISTS (SELECT 1 FROM api_settings WHERE name = 'chat_history_turns')"
    )


def downgrade() -> None:
    """Removes chat entirely, including all stored conversations."""
    op.execute("DELETE FROM api_settings WHERE name = 'chat_history_turns'")
    op.drop_column('group_vdbs', 'gvdbs_chat_cfg')
    op.drop_column('api_groups', 'chat_rewrite_gllms_id')
    op.drop_column('api_groups', 'chat_enabled')
    op.drop_table('chat_messages')
    op.drop_index('ix_chat_conversations_user_id_updated_at', table_name='chat_conversations')
    op.drop_table('chat_conversations')
