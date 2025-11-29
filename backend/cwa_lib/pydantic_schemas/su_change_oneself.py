from pydantic import BaseModel


class SuChangeOneselfGroup(BaseModel):
    group_id: int
    group_name: str


class SuChangeOneselfGetResult(BaseModel):
    group_list: list[SuChangeOneselfGroup]
    group_id: int
    is_groupadmin: bool
    is_contentmanager: bool    


class SuChangeOneselfUpdate(BaseModel):
    group_id: int
    is_groupadmin: bool
    is_contentmanager: bool

class SuChangeOneselfUpdateResult(BaseModel):
    is_success: bool
    error_msg: str | None = None
    group_id: int | None = None
    is_groupadmin: bool | None = None
    is_content_manager: bool | None = None
