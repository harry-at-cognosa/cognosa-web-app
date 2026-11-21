from datetime import datetime
from sqlalchemy import Integer, Text, VARCHAR, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class ChatConversations(Base):
    """One conversation on the Chat page.

    A conversation is bound to one collection (`gvdbs_id`) and one set of
    retrieval filter values (`filters_json`); both are fixed at creation.
    Rows are hard-deleted: there is no `deleted` flag.
    """
    __tablename__ = "chat_conversations"
    __table_args__ = (
        Index('ix_chat_conversations_user_id_updated_at', 'user_id', 'updated_at'),
    )

    conv_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_groups.group_id", name="fk_chat_conversations_group_id"), nullable=False)
    # api_users.user_id (owner)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default="")
    # group_vdbs.gvdbs_id: the conversation's collection, fixed
    gvdbs_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Retrieval filter values, same shape as `filters` in doc_tasks.gvdbs_cfg_json.
    # NULL when the collection has no filters or none were set. Fixed.
    filters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # group_llms.gllms_id: last used LLM, the default for the next turn
    gllms_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
