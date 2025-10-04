from datetime import datetime
from sqlalchemy import Integer, Text, VARCHAR, DateTime, text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class DocTasks(Base):
    __tablename__ = "doc_tasks"

    # doc_task_id SERIAL primary key semantics (auto-increment)
    doc_task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # group_id INT
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("api_groups.group_id", name="fk_api_users_group_id"), nullable=False) 

    # user_id INT
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # status INT DEFAULT 0
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    # status_text TEXT
    status_text: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))

    # short_name VARCHAR
    short_name: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))

    # input_text TEXT
    input_text: Mapped[str] = mapped_column(Text, nullable=False)

    # optional_text TEXT
    optional_text: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))

    # group_vdbs.gvdbs_id
    gvdbs_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # group_llms.gllms_id
    gllms_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # gc_id Foreign Key to group_contexts.gc_id
    gc_id: Mapped[int] = mapped_column(Integer, ForeignKey('group_contexts.gc_id'), nullable=False)

    # context_json TEXT
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # output_text TEXT
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # exc_text TEXT
    exc_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # created_at UTC datetime
    # Force UTC at the DB level
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        server_default=func.now()
    )
    # fetched_at UTC datetime
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # context_at UTC datetime
    context_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # completed_at UTC datetime
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
