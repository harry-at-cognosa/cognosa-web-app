from datetime import datetime
import re
import uuid
from fastapi_users import schemas
from pydantic import BaseModel, Field, field_validator

USERNAME_REGEX = re.compile(r"^[a-z0-9_-]+$")

def validate_user_name(v: str) -> str:
    v = v.lower()
    if not USERNAME_REGEX.match(v):
        raise ValueError("user_name must contain only lowercase letters, numbers, underscores, or hyphens")
    return v

class UserRead(schemas.BaseUser[uuid.UUID]):
    user_id: int
    group_id: int
    user_name: str
    full_name: str
    created_at: datetime | None = None


class UserCreate(schemas.BaseUserCreate):
    user_id: int | None = None
    group_id: int
    user_name: str = Field(..., min_length=3, max_length=32)
    full_name: str
    created_at: datetime | None = None
    is_groupadmin: bool = False
    is_contentmanager: bool = False

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        return validate_user_name(v)

class UserUpdate(schemas.BaseUserUpdate):
    user_id: int
    group_id: int
    user_name: str | None = None
    full_name: str
    created_at: datetime | None = None
    
    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_user_name(v)
    

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
