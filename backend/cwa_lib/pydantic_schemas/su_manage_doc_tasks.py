from datetime import datetime
from pydantic import BaseModel
from .generic_table import TableQueryResult


class SuManageDocTaskRead(BaseModel):
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
    gvdbs_json: str
    gllms_id: int
    gllms_json: str
    gc_id: int
    context_json: str | None
    sent_to_llm: str | None
    output_text: str | None
    question_number: int
    output_text_2: str | None
    exc_text: str | None
    created_at: datetime
    fetched_at: datetime | None
    completed_at: datetime | None
    vdb_query_seconds: float | None = None
    llm_query_seconds: float | None = None
    llm_tokens_sent: int | None = None
    llm_tokens_received: int | None = None

    model_config = {"from_attributes": True}

SuManageDocTasksQueryResult = TableQueryResult[SuManageDocTaskRead]
