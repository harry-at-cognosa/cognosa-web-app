from datetime import datetime
from sqlalchemy import DateTime, VARCHAR, Integer, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.sql_models import Base


class ApiGroups(Base):
    __tablename__ = "api_groups"
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_name: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("'Undefined group'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    api_users_id_list: Mapped[list["User"]] = relationship("User", back_populates="api_groups_id") # pyright: ignore[reportUndefinedVariable]
    group_contexts_id_list: Mapped[list["GroupContexts"]] = relationship(   # pyright: ignore[reportUndefinedVariable]
        "GroupContexts", back_populates="api_groups_id")
    group_vdbs_id_list: Mapped[list["GroupVDBs"]] = relationship(   # pyright: ignore[reportUndefinedVariable]
        "GroupVDBs", back_populates="api_groups_id")
    group_llms_id_list: Mapped[list["GroupLLMs"]] = relationship(   # pyright: ignore[reportUndefinedVariable]
        "GroupLLMs", back_populates="api_groups_id")
