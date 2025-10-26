from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from .generic_table import TableQueryResult

USERNAME_REGEX = re.compile(r"^[a-z0-9_-]+$")

def validate_user_name(v: str) -> str:
    v = v.lower()
    if not USERNAME_REGEX.match(v):
        raise ValueError("user_name must contain only lowercase letters, numbers, underscores, or hyphens")
    return v


class GaManageUsersRead(BaseModel):
    user_id: int
    user_name: str
    full_name: str
    email: str
    password: str | None = None
    created_at: datetime
    is_active: bool
    is_contentmanager: bool
    is_groupadmin: bool
    class Config:
        from_attributes = True


GaManageUsersQueryResult = TableQueryResult[GaManageUsersRead]


class GaManageUsersCreate(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=32)
    full_name: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: bool
    is_contentmanager: bool
    is_groupadmin: bool

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        return validate_user_name(v)


class GaManageUsersUpdate(BaseModel):
    user_id: int
    user_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_contentmanager: bool | None = None
    is_groupadmin: bool | None = None

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        return validate_user_name(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        # If password is specified, check minimum 8 characters length
        if v:
            v = str(v).strip()
        if v and (len(v) < 8):
            raise ValueError("password must be minimum 8 characters length")
        return v
