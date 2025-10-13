from typing import Generic, TypeVar, Sequence, Literal
from pydantic import BaseModel


class ColumnType(BaseModel):
    display: str | None
    seqn: int | None  # seqn = None - means invisible
    type: str
    default: str | int | bool | None = None


class TableOptions(BaseModel):
    title: str
    pk: str
    create__allow: bool
    create__ask_columns: list[str] = []  # on button Add, ask this column names values
    read__hide_on_false: list[str] = []  # table view: hide value if false
    update__allow: bool
    update__ask_columns: list[str] = []  # on button Update, ask this column names values
    delete__allow: bool
    delete__ask_columns: list[str] = []  # on button Delete, ask this column names values
    order_by__allow: list[str] = []


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


class TableCreateRowResult(BaseModel):
    result: str
    total_created: int


class TableUpdateRowResult(BaseModel):
    result: str
    total_updated: int


class TableDeleteRowResult(BaseModel):
    result: str
    total_deleted: int
