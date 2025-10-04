from datetime import datetime
from sqlalchemy import VARCHAR, Text, Integer, DateTime, func, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class ApiProcesses(Base):
    __tablename__ = "api_processes"
    
    # ap_id INTEGER PRIMARY KEY SERIAL
    ap_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # ap_type VARCHAR
    ap_type: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    # ap_name VARCHAR
    ap_name: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    # ap_subname VARCHAR 
    ap_subname: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))
    # ap_status VARCHAR
    ap_status: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))
    # ap_json VARCHAR
    ap_json: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'{}'"))
    # ap_updated_at DATETIME NOW
    ap_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # UNIQUE KEY (ap_name, ap_subname)
    __table_args__ = (
        UniqueConstraint('ap_name', 'ap_subname', name='ap_uix'),
    )
