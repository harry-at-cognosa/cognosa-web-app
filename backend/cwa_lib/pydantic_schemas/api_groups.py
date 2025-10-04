from pydantic import BaseModel


class GroupCreate(BaseModel):
    group_id: int
    group_name: str
