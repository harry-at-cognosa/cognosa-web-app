from pydantic import BaseModel, field_validator
from common.features.gvdbs_retr_params import GVDBsDefRetrParams


class GaGVDBsRetrParamsPut(BaseModel):
    gvdbs_retr_params: str
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str) -> str:
        GVDBsDefRetrParams.from_dict(v)
        return v