from datetime import datetime
from pydantic import BaseModel, Field
from common.features.gvdbs_retr_filters import RequestGVDBsRetrFilters


class ChatOptionsCollection(BaseModel):
    gvdbs_id: int
    gvdbs_name: str
    gvdbs_status: str
    # filter schema of the collection (JSON string, '{}' when it has no filters)
    gvdbs_retr_filters: str


class ChatOptionsLLM(BaseModel):
    gllms_id: int
    gllms_name: str
    gllms_status: str


class ChatOptions(BaseModel):
    collections: list[ChatOptionsCollection]
    llms: list[ChatOptionsLLM]


class ConversationCreate(BaseModel):
    gvdbs_id: int
    gllms_id: int
    # filter values for the whole conversation; fixed once created
    filters: RequestGVDBsRetrFilters | None = None


class MessageCreate(BaseModel):
    content: str
    # the LLM for this turn; may differ from turn to turn
    gllms_id: int


class ConversationRename(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class ConversationRead(BaseModel):
    conv_id: int
    title: str
    gvdbs_id: int
    gllms_id: int
    # validated filter values as stored, or None
    filters: dict | None = None
    created_at: datetime
    updated_at: datetime


class MessageRead(BaseModel):
    msg_id: int
    seqn: int
    role: str
    content: str
    status: str
    gllms_id: int | None = None
    retrieval_query: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    seconds: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationRead):
    messages: list[MessageRead]


class DeleteResult(BaseModel):
    conv_id: int
    success: bool
