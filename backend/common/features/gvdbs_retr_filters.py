from typing import Literal, Annotated, TypeAlias
from pydantic import BaseModel, Field, field_validator

###
# Pydantic model
###
class FieldBaseGVDBsRF(BaseModel):
    title: str
    path: str
    sub_type: str | None = None

class StringFieldGVDBsRF(FieldBaseGVDBsRF):
    type: Literal["string"]
    max_length: int = Field(gt=0)

class SelectFieldGVDBsRF(FieldBaseGVDBsRF):
    type: Literal["select"]
    values: list[str]
    default: str
    max_select: int

    @field_validator("max_select")
    @classmethod
    def validate_max_select(cls, v):
        # -1 means unlimited, otherwise must be >= 1
        if v != -1 and v < 1:
            raise ValueError("max_select must be -1 or >= 1")
        return v

    @field_validator("default")
    @classmethod
    def default_must_be_in_values(cls, v, info):
        values = info.data.get("values", [])
        if v not in values:
            raise ValueError("default must be one of values")
        return v

FieldGVDBsRF: TypeAlias = Annotated[StringFieldGVDBsRF | SelectFieldGVDBsRF, Field(discriminator="type")]

class FormSchemaGVDBsRF(BaseModel):
    enable_global_not: bool
    fields: list[FieldGVDBsRF]
