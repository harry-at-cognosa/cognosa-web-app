from pydantic import BaseModel
from .generic_table import TableQueryResult


class ManageVDBsRead(BaseModel):
    gvdbs_id: int
    group_id: int
    gvdbs_seqn: int
    gvdbs_type: str
    gvdbs_name: str
    gvdbs_url: str
    gvdbs_collection: str
    gvdbs_status: str
    gvdbs_status_text: str
    class Config:
        from_attributes = True


ManageVDBsQueryResult = TableQueryResult[ManageVDBsRead]


class ManageVDBsCreate(BaseModel):
    group_id: int
    gvdbs_seqn: int | None = None
    gvdbs_type: str
    gvdbs_name: str
    gvdbs_url: str
    gvdbs_collection: str


class ManageVDBsUpdate(BaseModel):
    gvdbs_id: int
    group_id: int | None = None
    gvdbs_seqn: int | None = None
    gvdbs_type: str | None = None
    gvdbs_name: str | None = None
    gvdbs_url: str | None = None
    gvdbs_collection: str | None = None
