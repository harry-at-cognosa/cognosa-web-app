from pydantic import BaseModel, field_validator, ValidationInfo
from common.features.chat_cfg import CHAT_HISTORY_TURNS_MAX
from .generic_table import TableQueryResult
from cwa_lib.validators.api_settings import validate__name


def validate__value(v: str, info: ValidationInfo) -> str:
    """Per-setting checks on the value. `name` is validated first, so it is in info.data."""
    if info.data.get('name') == 'chat_history_turns':
        try:
            n = int(str(v).strip())
        except Exception:
            raise ValueError(f"Enter a whole number from 1 to {CHAT_HISTORY_TURNS_MAX}") from None
        if not (1 <= n <= CHAT_HISTORY_TURNS_MAX):
            raise ValueError(f"Enter a whole number from 1 to {CHAT_HISTORY_TURNS_MAX}")
        return str(n)
    return v


class SuManageApiSettingsRead(BaseModel):
    name: str
    value: str
    class Config:
        from_attributes = True


SuManageApiSettingsQueryResult = TableQueryResult[SuManageApiSettingsRead]

class SuManageApiSettingsCreate(BaseModel):
    name: str
    value: str
    @field_validator("name")
    @classmethod
    def validate__name(cls, v: str) -> str:
        return validate__name(v)
    @field_validator("value")
    @classmethod
    def validate__value(cls, v: str, info: ValidationInfo) -> str:
        return validate__value(v, info)


class SuManageApiSettingsUpdate(BaseModel):
    name: str
    value: str
    @field_validator("name")
    @classmethod
    def validate__name(cls, v: str) -> str:
        return validate__name(v)
    @field_validator("value")
    @classmethod
    def validate__value(cls, v: str, info: ValidationInfo) -> str:
        return validate__value(v, info)