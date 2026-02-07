from sqlalchemy import Integer, VARCHAR, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base

class GroupVDBsSelectValues(Base):
    __tablename__ = "group_vdbs_select_values"
    # PK
    gvsv_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # group_vdbs.gvdbs_id
    gvdbs_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    # 1 - means metadata refresh for select auto-fill values
    gvsv_path: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    # 0 - new task. 
    gvsv_value: Mapped[str] = mapped_column(VARCHAR, nullable=False)
