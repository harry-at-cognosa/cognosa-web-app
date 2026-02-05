from typing import Literal, Annotated, TypeAlias
from pydantic import BaseModel, Field, field_validator, model_validator
import re

###
# Pydantic model
###
class FieldBaseGVDBsRF(BaseModel):
    title: str
    path: str
    sub_type: str | None = None
    rf_field_id: str
    @field_validator("rf_field_id")
    @classmethod
    def validate__rf_field_id(cls, v):
        if v is not None:
            # Pattern: alphanumeric, underscore, hyphen, minimum 2 characters
            if not re.match(r'^[a-zA-Z0-9_-]{2,}$', v):
                raise ValueError("rf_field_id must contain only letters, numbers, underscores, and hyphens, and be at least 2 characters long")
        return v

class StringFieldGVDBsRF(FieldBaseGVDBsRF):
    type: Literal["string"]
    max_length: int = Field(gt=0)

class SelectFieldGVDBsRF(FieldBaseGVDBsRF):
    type: Literal["select"]
    values: list[str]
    max_select: int

    @field_validator("max_select")
    @classmethod
    def validate__max_select(cls, v):
        # -1 means unlimited, otherwise must be >= 1
        if v != -1 and v < 1:
            raise ValueError("max_select must be -1 or >= 1")
        return v

FieldGVDBsRF: TypeAlias = Annotated[StringFieldGVDBsRF | SelectFieldGVDBsRF, Field(discriminator="type")]

class FormSchemaGVDBsRF(BaseModel):
    global_not_enabled: bool
    fields: list[FieldGVDBsRF]
    @model_validator(mode="after")
    def validate_unique_rf_field_ids(self):
        rf_field_ids = [field.rf_field_id for field in self.fields if field.rf_field_id is not None]
        
        if len(rf_field_ids) != len(set(rf_field_ids)):
            # Find duplicates for a better error message
            seen = set()
            duplicates = set()
            for rf_id in rf_field_ids:
                if rf_id in seen:
                    duplicates.add(rf_id)
                seen.add(rf_id)
            raise ValueError(f"rf_field_id must be unique. Duplicates found: {duplicates}")
        
        return self
    

class RequestGVDBsRetrFiltersValuesEntry(BaseModel):
  rf_field_id: str
  values_list: list[str]


class RequestGVDBsRetrFilters(BaseModel):
    global_not_value: bool | None = None
    values: list[RequestGVDBsRetrFiltersValuesEntry]


class GVDBsRetrFiltersFunctions:
    @staticmethod
    def check_user_request(user_filters: RequestGVDBsRetrFilters, gvdbs_retr_filters_str: str) -> dict | None:
        """
        Check user request filters to be valid for group_vdbs.gvdbs_retr_filters:
        1) must have rf_field_id specified in gvdbs_retr_filters
        2) must have unique rf_field_id values
        3) strings must be not empty
        4) select values must be in gvdbs_retr_filters
        """
        gvdbs_retr_filters = FormSchemaGVDBsRF.model_validate_json(gvdbs_retr_filters_str)
        global_not_enabled = gvdbs_retr_filters.global_not_enabled
        global_not_value = bool(user_filters.global_not_value) if global_not_enabled else None
        rf_field_id__field = {x.rf_field_id: x for x in gvdbs_retr_filters.fields}
        new_fields = []
        used_rf_field_ids = set()
        for user_field in user_filters.values:
            rf_field_id = user_field.rf_field_id
            if rf_field_id in used_rf_field_ids:
                continue
            if source_field := rf_field_id__field.get(rf_field_id):
                user_values_list = []
                if source_field.type == 'string':
                    user_values_list = [x.strip() for x in user_field.values_list if x.strip()]
                elif source_field.type == 'select':
                    user_values_list = [x for x in user_field.values_list if (x in source_field.values)]
                if user_values_list:
                    new_fields.append({'rf_field_id': rf_field_id, 'values_list': user_values_list})
                    used_rf_field_ids.add(rf_field_id)
        if not new_fields:
            return None
        if global_not_value is None:
            return {'values': new_fields}
        return {
            'global_not_value': global_not_value,
            'values': new_fields
        }
