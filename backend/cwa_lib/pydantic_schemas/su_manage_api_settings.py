from pydantic import BaseModel
from .generic_table import TableQueryResult


class SuManageApiSettingsRead(BaseModel):
    name: str
    value: str
    class Config:
        from_attributes = True


SuManageApiSettingsQueryResult = TableQueryResult[SuManageApiSettingsRead]


class SuManageApiSettingsUpdate(BaseModel):
    name: str
    value: str
