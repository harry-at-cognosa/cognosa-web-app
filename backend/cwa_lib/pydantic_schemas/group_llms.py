from pydantic import BaseModel
from .generic_table import TableQueryResult


class GroupLLMsRead(BaseModel):
    gllms_id: int
    group_id: int
    gllms_name: str
    gllms_status: str
    class Config:
        from_attributes = True


ManageGroupLLMsQueryResult = TableQueryResult[GroupLLMsRead]
