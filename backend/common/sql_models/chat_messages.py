from datetime import datetime
from sqlalchemy import Integer, Text, VARCHAR, DateTime, ForeignKey, UniqueConstraint, FLOAT, func
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class ChatMessageRole:
    USER = 'user'
    ASSISTANT = 'assistant'


class ChatMessageStatus:
    COMPLETE = 'complete'
    STOPPED = 'stopped'   # the user stopped the answer; `content` holds the partial text
    ERROR = 'error'       # retrieval or LLM failure; `content` holds the message shown


class ChatMessages(Base):
    """One message of a conversation: a user question or an assistant answer.

    Deliberately lean: nothing about retrieval results (chunks, ids, scores)
    and no assembled prompt is stored.
    """
    __tablename__ = "chat_messages"
    __table_args__ = (
        UniqueConstraint('conv_id', 'seqn', name='uq_chat_messages_conv_id_seqn'),
    )

    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conv_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat_conversations.conv_id", name="fk_chat_messages_conv_id", ondelete="CASCADE"),
        nullable=False)
    # order within the conversation, starting at 1
    seqn: Mapped[int] = mapped_column(Integer, nullable=False)
    # ChatMessageRole
    role: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    # ChatMessageStatus
    status: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, server_default=ChatMessageStatus.COMPLETE)
    # The columns below are set on assistant messages only.
    # group_llms.gllms_id: the LLM that wrote this answer
    gllms_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # the standalone question actually searched (the rewritten user message)
    retrieval_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seconds: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
