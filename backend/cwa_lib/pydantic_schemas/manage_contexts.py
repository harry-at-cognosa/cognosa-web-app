from pydantic import BaseModel
from .generic_table import TableQueryResult


class ManageContextsRead(BaseModel):
    gc_id: int
    group_id: int
    gc_seqn: int
    gc_name: str
    gc_text: str
    class Config:
        from_attributes = True


ManageContextsQueryResult = TableQueryResult[ManageContextsRead]


class ManageContextsCreate(BaseModel):
    gc_seqn: int | None = None
    gc_name: str
    gc_text: str


class ManageContextsUpdate(BaseModel):
    gc_id: int
    gc_seqn: int | None = None
    gc_name: str | None = None
    gc_text: str | None = None
