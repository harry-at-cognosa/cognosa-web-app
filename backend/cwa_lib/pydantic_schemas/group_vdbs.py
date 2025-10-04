from pydantic import BaseModel
from .generic_table import TableQueryResult


class GroupVDBSRead(BaseModel):
    gvdbs_id: int
    group_id: int
    gvdbs_name: str
    gvdbs_status: str
    class Config:
        from_attributes = True


ManageGroupVDBSQueryResult = TableQueryResult[GroupVDBSRead]
