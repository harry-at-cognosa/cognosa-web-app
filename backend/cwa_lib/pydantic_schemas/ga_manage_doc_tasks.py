from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from .generic_table import TableQueryResult

type_ga_status_str = Literal['completed', 'pending', 'error']

class GaManageDocTaskRead(BaseModel):
    doc_task_id: int
    user_id: int
    user_id_name: str
    status_str: type_ga_status_str
    short_name: str
    input_text: str
    optional_text: str
    gvdbs_name: str
    gvdbs_cfg: str
    gllms_name: str
    context_json: str | None
    sent_to_llm: str | None
    output_text: str | None
    question_number: int
    output_text_2: str | None
    created_at: datetime
    vdb_query_seconds: float | None = None
    llm_query_seconds: float | None = None
    llm_tokens_sent: int | None = None
    llm_tokens_received: int | None = None

    model_config = {"from_attributes": True}

GaManageDocTasksQueryResult = TableQueryResult[GaManageDocTaskRead]
