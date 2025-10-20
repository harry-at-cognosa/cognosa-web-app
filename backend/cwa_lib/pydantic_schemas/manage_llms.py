from pydantic import BaseModel
from .generic_table import TableQueryResult


class ManageLLMsRead(BaseModel):
    gllms_id: int
    group_id: int
    gllms_seqn: int
    gllms_type: str
    gllms_name: str
    gllms_api_base: str
    gllms_model: str
    gllms_api_key: str
    gllms_status: str
    gllms_status_text: str
    class Config:
        from_attributes = True


ManageLLMsQueryResult = TableQueryResult[ManageLLMsRead]


class ManageLLMsCreate(BaseModel):
    group_id: int
    gllms_seqn: int | None = None
    gllms_type: str
    gllms_name: str
    gllms_api_base: str
    gllms_model: str
    gllms_api_key: str


class ManageLLMsUpdate(BaseModel):
    gllms_id: int
    group_id: int | None = None
    gllms_seqn: int | None = None
    gllms_type: str | None = None
    gllms_name: str | None = None
    gllms_api_base: str | None = None
    gllms_model: str | None = None
    gllms_api_key: str | None = None
