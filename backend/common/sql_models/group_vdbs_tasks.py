from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base

class GroupVDBsTasks(Base):
    __tablename__ = "group_vdbs_tasks"
    __table_args__ = (
        UniqueConstraint('gvdbs_id', 'gvt_type', name='uq_gvdbs_id_gvt_type'),
    )
    
    # PK
    gvt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # group_vdbs.gvdbs_id
    gvdbs_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # 1 - means metadata refresh for select auto-fill values
    gvt_type: Mapped[int] = mapped_column(Integer, nullable=False)
    # 0 - new task. 
    gvt_status: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
