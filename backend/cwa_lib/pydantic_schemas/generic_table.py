from typing import Generic, TypeVar, Sequence, Literal
from pydantic import BaseModel


class ColumnType(BaseModel):
    display: str | None
    seqn: int | None  # seqn = None - means invisible
    type: str


class TableOptions(BaseModel):
    title: str
    pk: str
    allow_add: bool
    allow_update: bool
    allow_delete: bool
    delete_ask_column: str = ''  # on button Delete, ask this column name value
    allow_order_by: list[str] = []


class TableQuery(BaseModel):
    name: str
    order_by: str | None = None
    order_dir: Literal['asc', 'desc'] | None = None
    limit: int | None = None
    offset: int | None = None


RowType = TypeVar("RowType")

class TableQueryResult(BaseModel, Generic[RowType]):
    name: str
    rows: Sequence[RowType]
    columns: dict[str, ColumnType]
    table_options: TableOptions
    total: int
