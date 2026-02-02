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