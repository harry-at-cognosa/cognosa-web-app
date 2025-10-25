from pydantic import BaseModel
from .generic_table import TableQueryResult


class SuManageLLMsRead(BaseModel):
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


SuManageLLMsQueryResult = TableQueryResult[SuManageLLMsRead]


class SuManageLLMsCreate(BaseModel):
    group_id: int
    gllms_seqn: int | None = None
    gllms_type: str
    gllms_name: str
    gllms_api_base: str
    gllms_model: str
    gllms_api_key: str


class SuManageLLMsUpdate(BaseModel):
    gllms_id: int
    group_id: int | None = None
    gllms_seqn: int | None = None
    gllms_type: str | None = None
    gllms_name: str | None = None
    gllms_api_base: str | None = None
    gllms_model: str | None = None
    gllms_api_key: str | None = None
