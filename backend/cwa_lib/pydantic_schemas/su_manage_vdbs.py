import json
from pydantic import BaseModel, field_validator, ValidationError
from .generic_table import TableQueryResult
from common.features.gvdbs_retr_filters import FormSchemaGVDBsRF
from common.features.gvdbs_retr_params import GVDBsDefRetrParams


class SuManageVDBsRead(BaseModel):
    gvdbs_id: int
    group_id: int
    enabled: bool
    gvdbs_seqn: int
    gvdbs_type: str
    gvdbs_name: str
    gvdbs_url: str
    gvdbs_collection: str
    gvdbs_retr_params: str
    rf_refresh_metadata: bool = False
    gvdbs_retr_filters: str
    gvdbs_status: str
    gvdbs_status_text: str
    class Config:
        from_attributes = True


SuManageVDBsQueryResult = TableQueryResult[SuManageVDBsRead]


class SuManageVDBsCreate(BaseModel):
    group_id: int
    enabled: bool
    gvdbs_seqn: int | None = None
    gvdbs_type: str
    gvdbs_name: str
    gvdbs_url: str
    gvdbs_collection: str
    gvdbs_retr_filters: str
    @field_validator('gvdbs_retr_filters')
    @staticmethod
    def validate__gvdbs_retr_filters(v: str) -> str:
        if v == '{}':
            return v
        try:
            data = json.loads(v)
        except Exception:
            raise ValueError('JSON string expected') from None
        try:
            FormSchemaGVDBsRF.model_validate(data)
        except ValidationError as exc:
            raise ValueError(str(exc)) from None
        return v

class SuManageVDBsUpdate(BaseModel):
    gvdbs_id: int
    group_id: int | None = None
    enabled: bool | None = None
    gvdbs_seqn: int | None = None
    gvdbs_type: str | None = None
    gvdbs_name: str | None = None
    gvdbs_url: str | None = None
    gvdbs_collection: str | None = None
    gvdbs_retr_params: str | None = None
    rf_refresh_metadata: bool | None = None
    gvdbs_retr_filters: str | None = None
    @field_validator('gvdbs_retr_params')
    @staticmethod
    def validate__gvdbs_retr_params(v: str | None) -> str | None:
        if v is not None:
            GVDBsDefRetrParams.from_dict(v)
        return v
    @field_validator('gvdbs_retr_filters')
    @staticmethod
    def validate__gvdbs_retr_filters(v: str | None) -> str | None:
        if v is not None:
            if v == '{}':
                return v
            try:
                data = json.loads(v)
            except Exception:
                raise ValueError('JSON string expected') from None
            try:
                FormSchemaGVDBsRF.model_validate(data)
            except ValidationError as exc:
                raise ValueError(str(exc)) from None
        return v