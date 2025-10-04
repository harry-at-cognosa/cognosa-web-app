from datetime import datetime
from pydantic import BaseModel
from typing import Sequence


class DocTaskCreate(BaseModel):
    short_name: str
    input_text: str
    optional_text: str
    gvdbs_id: int
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
    gc_id: int
    output_text: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
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
