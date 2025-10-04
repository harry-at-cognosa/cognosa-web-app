from pydantic import BaseModel
from .generic_table import TableQueryResult


class GroupContextsCreate(BaseModel):
    group_id: int
    gc_seqn: int
    gc_name: str
    gc_text: str


class GroupContextsRead(BaseModel):
    gc_id: int
    group_id: int
    gc_seqn: int
    gc_name: str
    gc_text: str
    class Config:
        from_attributes = True


ManageContextsQueryResult = TableQueryResult[GroupContextsRead]
