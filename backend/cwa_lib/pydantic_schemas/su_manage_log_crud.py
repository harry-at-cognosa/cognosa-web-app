from datetime import datetime
from pydantic import BaseModel
from .generic_table import TableQueryResult


class SuManageLogCRUDRead(BaseModel):
    lc_id: int
    dt: datetime
    group_id: int
    user_id: int
    user_name: str
    source_addr: str
    method: str
    dest_addr: str
    data: str
    result: str | None
    
    model_config = {"from_attributes": True}

SuManageLogCRUDQueryResult = TableQueryResult[SuManageLogCRUDRead]
