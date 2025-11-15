import re
from pydantic import BaseModel, field_validator, Field
from .generic_table import TableQueryResult
from cwa_lib.validators.strings import StringValidator
from cwa_lib.validators.messages import msg_no_special_symbols


class ManageContextsRead(BaseModel):
    gc_id: int
    group_id: int
    gc_seqn: int
    gc_name: str
    gc_text: str
    class Config:
        from_attributes = True


ManageContextsQueryResult = TableQueryResult[ManageContextsRead]

def validate__gc_text(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError('Must be string')
    v = v.strip()
    for template in ('{context}', '{question}'):
        count = v.count(template)       
        if count == 0:
            raise ValueError(f'Required "{template}" not found')
        elif count > 1:
            raise ValueError(f'"{template}" appears {count} times, but must appear exactly once')
    return v

description__gc_name = msg_no_special_symbols
description__gc_text = "Must have {context} and {question} template strings."

class ManageContextsCreate(BaseModel):
    gc_seqn: int | None = None
    gc_name: str = Field(..., description=description__gc_name)
    gc_text: str = Field(..., description=description__gc_text)
    @field_validator('gc_name')
    @classmethod
    def validate__gc_name(cls, v: str) -> str:
        return StringValidator.replace_non_common_lang(v, min_length=3, max_length=100)
    # gc_text must contain {context} and {question} templates
    @field_validator('gc_text')
    @classmethod
    def validate__gc_text(cls, v: str) -> str:
        return validate__gc_text(v)

class ManageContextsUpdate(BaseModel):
    gc_id: int
    gc_seqn: int | None = None
    gc_name: str | None = Field(None, description=description__gc_name)
    gc_text: str | None = Field(None, description=description__gc_text)
    @field_validator('gc_name')
    @classmethod
    def validate__gc_name(cls, v: str | None) -> str | None:
        if not v:
            return None
        return StringValidator.replace_non_common_lang(v, min_length=3, max_length=100)
    
    @field_validator('gc_text')
    @classmethod
    def validate__gc_text(cls, v: str | None) -> str | None:
        if not v:
            return None
        return validate__gc_text(v)
