from datetime import datetime
from pydantic import BaseModel
from typing import Sequence

class DocTaskCreate(BaseModel):
    doc_task_id: int | None
    short_name: str
    input_text: str
    optional_text: str
    gvdbs_id: int
    gvdbs_cfg_json: dict[str, str | dict[str, float | int]]
    gllms_id: int
    gc_id: int


class DocTaskQueryResult(BaseModel):
    doc_task_id: int
    group_id: int
    user_id: int
    status: int
    status_text: str
    short_name: str
    input_text: str
    optional_text: str
    gvdbs_id: int
    gvdbs_cfg_json: str
    gllms_id: int
    gc_id: int
    context_json: str | None = None
    output_text: str | None = None
    question_number: int
    output_text_2: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    vdb_query_seconds: float | None = None
    llm_query_seconds: float | None = None
    llm_tokens_sent: int | None = None
    llm_tokens_received: int | None = None
    is_processing: bool
    is_error: bool
    status_pct: int

    model_config = {"from_attributes": True}


class DocTaskDeleteResult(BaseModel):
    doc_task_id: int
    success: bool
    error_msg: str


class DocTaskQueryShortItem(BaseModel):
    doc_task_id: int
    status: int
    status_text: str
    short_name: str
    created_at: datetime
    is_processing: bool
    is_error: bool
    status_pct: int
    
    model_config = {"from_attributes": True}


class DocTaskQueryShort(BaseModel):
    rows: Sequence[DocTaskQueryShortItem]


class DocTasksOptionsGroupContextsRow(BaseModel):
    gc_id: int
    group_id: int
    gc_seqn: int
    gc_name: str
    gc_text: str
    class Config:
        from_attributes = True

class DocTasksOptionsGroupLLMsRow(BaseModel):
    gllms_id: int
    group_id: int
    gllms_seqn: int
    gllms_name: str
    gllms_status: str
    class Config:
        from_attributes = True

class DocTasksOptionsGroupVDBsRow(BaseModel):
    gvdbs_id: int
    group_id: int
    gvdbs_seqn: int
    gvdbs_name: str
    gvdbs_retr_params: str
    gvdbs_status: str
    class Config:
        from_attributes = True

class DocTaskOptionsResult(BaseModel):
    group_contexts: Sequence[DocTasksOptionsGroupContextsRow]
    group_llms: Sequence[DocTasksOptionsGroupLLMsRow]
    group_vdbs: Sequence[DocTasksOptionsGroupVDBsRow]
