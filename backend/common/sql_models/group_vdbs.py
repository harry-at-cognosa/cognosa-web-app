from datetime import datetime
from sqlalchemy import VARCHAR, Integer, Boolean, ForeignKey, DateTime, func, text, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.sql_models import Base
from common.enums.gvdbs_types import GVDBsTypes

# ['chroma', 'qdrant', 'pgvector', ...]
GVDBS_TYPE_VALUES = [v for k, v in vars(GVDBsTypes).items() if not k.startswith('_') and isinstance(v, str)]

class GroupVDBs(Base):
    __tablename__ = "group_vdbs"
    
    # gvdb_id Integer PRIMARY KEY
    gvdbs_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # deleted INT DEFAULT 0
    deleted: Mapped[int] = mapped_column(Integer, index=True, nullable=False, server_default=text("0"))
    enabled: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, server_default=text("'TRUE'"))    
    group_id = mapped_column(Integer, ForeignKey('api_groups.group_id', name="fk_group_vdbs_group_id"), nullable=False)
    gvdbs_seqn: Mapped[int] = mapped_column(Integer, nullable=False)
    # gvdbs_type = chroma / qdrant / pgvector
    gvdbs_type: Mapped[str] = mapped_column(SQLEnum(*GVDBS_TYPE_VALUES, name="gvdbs_type_enum"), nullable=False)
    gvdbs_name: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("'No database name'"))
    gvdbs_url: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gvdbs_collection: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gvdbs_retr_params: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gvdbs_emb_model: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gvdbs_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # gvdbs_status = success / warning / danger
    gvdbs_status: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("'warning'"))
    # more info:
    gvdbs_status_text: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))
    gvdbs_status_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 
    from common.sql_models import ApiGroups
    api_groups_id: Mapped["ApiGroups"] = relationship("ApiGroups", back_populates="group_vdbs_id_list")

    # index (group_id, gvdbs_seqn)
    __table_args__ = (
        Index('ix_group_vdbs_group_id_seqn', 'group_id', 'gvdbs_seqn'),
    )