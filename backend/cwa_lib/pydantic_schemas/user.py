from datetime import datetime
import uuid
from fastapi_users import schemas
from pydantic import BaseModel, Field


class UserRead(schemas.BaseUser[uuid.UUID]):
    user_id: int
    group_id: int
    full_name: str
    created_at: datetime | None = None


class UserCreate(schemas.BaseUserCreate):
    user_id: int | None = None
    group_id: int
    full_name: str
    created_at: datetime | None = None
    is_groupadmin: bool = False

class UserUpdate(schemas.BaseUserUpdate):
    user_id: int
    group_id: int
    full_name: str
    created_at: datetime | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
