from pydantic import BaseModel
from .generic_table import TableQueryResult


class ManageGroupsRead(BaseModel):
    group_id: int
    group_name: str
    
    class Config:
        from_attributes = True


ManageGroupsQueryResult = TableQueryResult[ManageGroupsRead]


class ManageGroupsCreate(BaseModel):
    group_name: str


class ManageGroupsUpdate(BaseModel):
    group_id: int
    group_name: str | None = None
