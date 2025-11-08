from typing import Generic, TypeVar, Sequence, Literal, Any
from pydantic import BaseModel


class SelectOption(BaseModel):
    name: str
    value: int | str


class ColumnType(BaseModel):
    display: str | None
    type: str
    default: str | int | bool | None = None
    select: list[SelectOption] | None = None


class TableOptions(BaseModel):
    title: str
    pk: str
    read__visible_columns: list[str] = []  # column sequence in table view
    read__hide_on_false: list[str] = []  # table view: hide value if false
    create__ask_columns: list[str] = []  # on button Add, ask this column names values
    update__ask_columns: list[str] = []  # on button Update, ask this column names values
    delete__ask_columns: list[str] = []  # on button Delete, ask this column names values
    order_by__allow: list[str] = []
    # additional values e.g. {'group_id_name': {<group_id>: <group_name>, ...}, ...}
    add_values: dict[str, Any] = dict()
    # default/max LIMIT
    default_limit: int = 20
    max_limit: int = 50


class TableQuery(BaseModel):
    name: str
    order_by: str | None = None
    order_dir: Literal['asc', 'desc'] | None = None
    limit: int | None = None
    offset: int | None = None


RowModel = TypeVar("RowModel", bound=BaseModel)

class TableQueryResult(BaseModel, Generic[RowModel]):
    name: str
    rows: Sequence[RowModel]
    columns: dict[str, ColumnType]
    table_options: TableOptions
    total: int
    limit: int = 20
    offset: int = 0
    order_by: str
    order_dir: Literal['asc', 'desc']


class TableCreateRowResult(BaseModel):
    result: str
    error_msg: str | None = None
    total_created: int


class TableUpdateRowResult(BaseModel):
    result: str
    error_msg: str | None = None
    total_updated: int


class TableDeleteRowResult(BaseModel):
    result: str
    error_msg: str | None = None
    total_deleted: int
