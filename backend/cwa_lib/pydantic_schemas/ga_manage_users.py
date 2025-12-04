from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from .generic_table import TableQueryResult
from cwa_lib.validators.strings import StringValidator
from cwa_lib.validators.user_name import validate_user_name


class GaManageUsersRead(BaseModel):
    user_id: int
    user_name: str
    full_name: str
    email: str
    password: str | None = None
    created_at: datetime
    last_seen: datetime | None
    is_active: bool
    is_contentmanager: bool
    is_groupadmin: bool
    class Config:
        from_attributes = True


GaManageUsersQueryResult = TableQueryResult[GaManageUsersRead]


class GaManageUsersCreate(BaseModel):
    user_name: str
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: bool
    is_contentmanager: bool
    is_groupadmin: bool

    @field_validator("user_name")
    @classmethod
    def validate__user_name(cls, v: str) -> str:
        return validate_user_name(v)
    @field_validator("full_name")
    @classmethod
    def validate__full_name(cls, v: str) -> str:
        return StringValidator.replace_non_common_lang(v, 3, 32)


class GaManageUsersUpdate(BaseModel):
    user_id: int
    user_name: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    is_contentmanager: bool | None = None
    is_groupadmin: bool | None = None

    @field_validator("user_name")
    @classmethod
    def validate__user_name(cls, v: str) -> str | None:
        if not v:
            return None
        return validate_user_name(v)
    
    @field_validator("full_name")
    @classmethod
    def validate__full_name(cls, v: str) -> str | None:
        if not v:
            return None
        return StringValidator.replace_non_common_lang(v, 3, 32)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        # If password is specified, check minimum 8 characters length
        if v:
            v = str(v).strip()
        if v and (len(v) < 8):
            raise ValueError("password must be minimum 8 characters length")
        return v
