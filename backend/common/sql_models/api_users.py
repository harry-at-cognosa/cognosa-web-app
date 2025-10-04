from datetime import datetime
import uuid
from typing import TYPE_CHECKING
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import DateTime, VARCHAR, Integer, Boolean, text, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.sql_models import Base


# Inherits id (UUID), email, hashed_password, is_active, is_superuser, is_verified
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'api_users'
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("api_groups.group_id", name="fk_api_users_group_id"), nullable=False, server_default=text("2"))    
    user_name: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(VARCHAR, nullable=False, server_default=text("''"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_groupadmin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("'FALSE'"))
    is_contentmanager: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("'FALSE'"))
    from common.sql_models import ApiGroups
    api_groups_id: Mapped["ApiGroups"] = relationship("ApiGroups", back_populates="api_users_id_list")
    # change id UUID from primary key to unique
    if TYPE_CHECKING:  # pragma: no cover
        id: uuid.UUID
    else:
        id: Mapped[uuid.UUID] = mapped_column(GUID, unique=True, default=uuid.uuid4)

    __table_args__ = (
        UniqueConstraint('user_name', name='uq_api_users_user_name'),
        CheckConstraint(
            "char_length(user_name) BETWEEN 3 AND 32 AND user_name ~ '^[a-z0-9_-]+$'",
            name="ck_api_users_user_name_format",
        ),
    )

