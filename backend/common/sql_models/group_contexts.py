from datetime import datetime
from sqlalchemy import VARCHAR, Integer, ForeignKey, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.sql_models import Base


class GroupContexts(Base):
    __tablename__ = "group_contexts"
    
    # gc_id Integer PRIMARY KEY
    gc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # deleted INT DEFAULT 0
    deleted: Mapped[int] = mapped_column(Integer, index=True, nullable=False, server_default=text("0"))
    group_id = mapped_column(Integer, ForeignKey('api_groups.group_id', name="fk_group_contexts_group_id"), nullable=False)
    gc_seqn = mapped_column(Integer, nullable=False)
    gc_name: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gc_text: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # 
    from common.sql_models import ApiGroups
    api_groups_id: Mapped["ApiGroups"] = relationship("ApiGroups", back_populates="group_contexts_id_list")
