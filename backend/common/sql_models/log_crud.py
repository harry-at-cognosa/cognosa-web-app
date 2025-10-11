from datetime import datetime
from sqlalchemy import DateTime, VARCHAR, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class LogCRUD(Base):
    __tablename__ = "log_crud"
    
    lc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_name: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    source_addr: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    method: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    dest_addr: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    data: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    result: Mapped[str] = mapped_column(VARCHAR, nullable=True)
