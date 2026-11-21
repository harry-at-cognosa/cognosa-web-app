from pydantic import BaseModel, field_validator
from .generic_table import TableQueryResult
from common.features.gvdbs_retr_params import GVDBsDefRetrParams

class SuManageGroupsRead(BaseModel):
    group_id: int
    group_name: str
    gvdbs_retr_params: str
    # Chat (conversation mode). These two exist only in the superuser schemas:
    # no group-admin route reads or writes them.
    chat_enabled: bool = False
    chat_rewrite_gllms_id: int | None = None
    
    class Config:
        from_attributes = True


SuManageGroupsQueryResult = TableQueryResult[SuManageGroupsRead]


class SuManageGroupsCreate(BaseModel):
    group_name: str
    gvdbs_retr_params: str
    chat_enabled: bool = False
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str) -> str:
        GVDBsDefRetrParams.from_dict(v)
        return v

class SuManageGroupsUpdate(BaseModel):
    group_id: int
    group_name: str | None = None
    gvdbs_retr_params: str | None = None
    chat_enabled: bool | None = None
    # When the key is sent, None (or 0) clears the setting: the conversation's own LLM is used.
    chat_rewrite_gllms_id: int | None = None
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str | None) -> str | None:
        if v is not None:
            GVDBsDefRetrParams.from_dict(v)
        return v
