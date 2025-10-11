from datetime import datetime
from sqlalchemy import VARCHAR, Integer, ForeignKey, DateTime, func, text, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.sql_models import Base
from common.enums.gllms_types import GLLMsTypes

# ['dummy', 'ollama_local', 'ollama_remote', ...]
GLLMS_TYPE_VALUES = [v for k, v in vars(GLLMsTypes).items() if not k.startswith('_') and isinstance(v, str)]

class GroupLLMs(Base):
    __tablename__ = "group_llms"
    
    # gvdb_id Integer PRIMARY KEY
    gllms_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # deleted INT DEFAULT 0
    deleted: Mapped[int] = mapped_column(Integer, index=True, nullable=False, server_default=text("0"))
    group_id = mapped_column(Integer, ForeignKey('api_groups.group_id', name="fk_group_llms_group_id"), nullable=False)
    gllms_seqn: Mapped[int] = mapped_column(Integer, nullable=False)
    # gllms_type = ollama_local / ollama_remote
    gllms_type: Mapped[str] = mapped_column(SQLEnum(*GLLMS_TYPE_VALUES, name="gllms_type_enum"), nullable=False)
    gllms_name: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("'No LLM name'"))
    gllms_api_base: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gllms_model: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gllms_api_key: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    gllms_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # gllms_status = success / warning / danger
    gllms_status: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("'warning'"))
    # more info:
    gllms_status_text: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))
    gllms_status_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    # 
    from common.sql_models import ApiGroups
    api_groups_id: Mapped["ApiGroups"] = relationship("ApiGroups", back_populates="group_llms_id_list")

    # index (group_id, gllms_seqn)
    __table_args__ = (
        Index('ix_group_llms_group_id_seqn', 'group_id', 'gllms_seqn'),
    )