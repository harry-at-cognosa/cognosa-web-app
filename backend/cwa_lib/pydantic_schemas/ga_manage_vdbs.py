from pydantic import BaseModel, Field, field_validator
from .generic_table import TableQueryResult
from common.features.gvdbs_retr_params import GVDBsDefRetrParams


class GaManageVDBsRead(BaseModel):
    gvdbs_id: int
    enabled: bool
    gvdbs_seqn: int
    gvdbs_name: str
    gvdbs_retr_params: str
    gvdbs_status: str
    gvdbs_status_text: str
    class Config:
        from_attributes = True


GaManageVDBsQueryResult = TableQueryResult[GaManageVDBsRead]


class GaManageVDBsUpdate(BaseModel):
    gvdbs_id: int
    enabled: bool | None = None
    gvdbs_seqn: int | None = None
    gvdbs_name: str | None = Field(default=None, max_length=100)
    gvdbs_retr_params: str | None = None
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str | None) -> str | None:
        if v is not None:
            GVDBsDefRetrParams.from_dict(v)
        return v