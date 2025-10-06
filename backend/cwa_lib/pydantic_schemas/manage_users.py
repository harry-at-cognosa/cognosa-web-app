from datetime import datetime
from pydantic import BaseModel
from .generic_table import TableQueryResult


class ManageUsersRead(BaseModel):
    user_id: int
    group_id: int
    user_name: str
    full_name: str
    email: str
    created_at: datetime
    is_active: bool
    is_contentmanager: bool
    is_groupadmin: bool
    is_superuser: bool
    class Config:
        from_attributes = True


ManageUsersQueryResult = TableQueryResult[ManageUsersRead]
