from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel


class ColumnType(BaseModel):
    display: str | None
    seqn: int | None  # seqn = None - means invisible
    type: str


RowType = TypeVar("RowType")

class TableQueryResult(BaseModel, Generic[RowType]):
    name: str
    rows: Sequence[RowType]
    columns: dict[str, ColumnType]
    total: int
