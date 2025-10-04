from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column
from common.sql_models import Base


class ApiSettings(Base):
    __tablename__ = "api_settings"
    
    # name VARCHAR PRIMARY KEY
    name: Mapped[str] = mapped_column(VARCHAR, primary_key=True)

    # value VARCHAR
    value: Mapped[str] = mapped_column(VARCHAR)
