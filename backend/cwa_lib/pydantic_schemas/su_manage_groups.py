from pydantic import BaseModel
from .generic_table import TableQueryResult


class SuManageGroupsRead(BaseModel):
    group_id: int
    group_name: str
    
    class Config:
        from_attributes = True


SuManageGroupsQueryResult = TableQueryResult[SuManageGroupsRead]


class SuManageGroupsCreate(BaseModel):
    group_name: str


class SuManageGroupsUpdate(BaseModel):
    group_id: int
    group_name: str | None = None
