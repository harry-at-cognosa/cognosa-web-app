from pydantic import BaseModel, field_validator
from .generic_table import TableQueryResult
from cwa_lib.validators.api_settings import validate__name


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


class SuManageApiSettingsUpdate(BaseModel):
    name: str
    value: str
    @field_validator("name")
    @classmethod
    def validate__name(cls, v: str) -> str:
        return validate__name(v)