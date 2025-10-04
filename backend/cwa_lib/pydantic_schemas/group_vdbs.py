from pydantic import BaseModel
from .generic_table import TableQueryResult


class GroupVDBsRead(BaseModel):
    gvdbs_id: int
    group_id: int
    gvdbs_name: str
    gvdbs_status: str
    class Config:
        from_attributes = True


ManageGroupVDBsQueryResult = TableQueryResult[GroupVDBsRead]
