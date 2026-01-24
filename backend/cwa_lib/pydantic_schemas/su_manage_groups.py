from pydantic import BaseModel, field_validator
from .generic_table import TableQueryResult
from common.features.gvdbs_retr_params import GVDBsDefRetrParams

class SuManageGroupsRead(BaseModel):
    group_id: int
    group_name: str
    gvdbs_retr_params: str
    
    class Config:
        from_attributes = True


SuManageGroupsQueryResult = TableQueryResult[SuManageGroupsRead]


class SuManageGroupsCreate(BaseModel):
    group_name: str
    gvdbs_retr_params: str
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str) -> str:
        GVDBsDefRetrParams.from_dict(v)
        return v

class SuManageGroupsUpdate(BaseModel):
    group_id: int
    group_name: str | None = None
    gvdbs_retr_params: str | None = None
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str | None) -> str | None:
        if v is not None:
            GVDBsDefRetrParams.from_dict(v)
        return v
