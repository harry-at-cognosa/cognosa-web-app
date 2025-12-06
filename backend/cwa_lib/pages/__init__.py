from copy import deepcopy
from typing import Generic, Literal, TypeVar
from sqlalchemy import select, func, ColumnElement
from sqlalchemy.orm import DeclarativeBase
from common.sql_tools import create_order_clause
from cwa_lib.pydantic_schemas.generic_table import (
    SelectOption, ColumnType, TableOptions, TableQuery, RowModel, TableQueryResult
)
from cwa_lib.sql_tables.api_users import ApiUsersTable, AsyncSession
from cwa_lib.sql_tables.api_groups import ApiGroupsTable

_UserGroupChoose = dict[Literal['user_id', 'group_id'], tuple[Literal['add_values', 'select_default', 'allow_all'], ...]]

SA = TypeVar("SA", bound=DeclarativeBase)

class GenericTableRead(Generic[SA, RowModel]):
    sa_model: type[SA]
    read_model: type[RowModel]
    name: str
    query_columns: dict[str, ColumnType]
    table_options: TableOptions
    default_order_by: str
    qc_to_user_group: _UserGroupChoose | None = None

    def __init__(self, session: AsyncSession, payload: TableQuery, **kwargs) -> None:
        self.session = session
        self.payload = payload
        self.kwargs = kwargs

        self._stmt = select(self.sa_model)
        self._stmt_total = select(func.count()).select_from(self.sa_model)
        self._limit: int = 0
        self._offset: int = 0
        self._total: int = 0
        self._order_dir: Literal['asc', 'desc'] = 'asc'
        self._to = self.table_options
        self._qc = self.query_columns

    def _create_order_clause(self):
        return create_order_clause(self.sa_model, self.default_order_by, self.payload.order_by, self.payload.order_dir)
    
    def _get_order_clause_by_dir(self):
        self._order_clause, self._order_by, self._order_dir = self._create_order_clause()
    
    def _get_where_clause(self) -> ColumnElement | None:
        return None
    
    def _add_where_clause(self) -> None:
        where_clause = self._get_where_clause()
        if where_clause is not None:
            self._stmt = self._stmt.where(where_clause)
            self._stmt_total = self._stmt_total.where(where_clause)
    
    async def _get_total(self):
        total = (await self.session.execute(self._stmt_total)).scalar()
        self._total = total if total else 0

    def _add_order_by(self):
        self._stmt = self._stmt.order_by(self._order_clause)

    def _add_limit_offset(self):
        self._limit = min(
            self._to.max_limit, 
            self.payload.limit if self.payload.limit else self._to.default_limit
        )
        self._limit = max(1, self._limit)
        self._stmt = self._stmt.limit(self._limit)
        self._offset = max(0, self.payload.offset if self.payload.offset else 0)
        if self._offset:
            self._stmt = self._stmt.offset(self._offset)

    async def _update_to_qc(self):
        if not self.qc_to_user_group:
            return
        # make deep copies, so they won't change class variables
        self._qc = deepcopy(self.query_columns)
        self._to = deepcopy(self.table_options)
        ###
        # Add non-deleted {user id: name, ...} values.
        # Add non-deleted {group id: name, ...} values.
        ###
        if user_opts := self.qc_to_user_group.get('user_id', ()):
            # update list of `api_users`.`user_id` and `api_users`.`user_name`
            all_user_rows = await ApiUsersTable(self.session).get_all_not_deleted()
            if 'allow_all' not in user_opts:  # restrict to fetched if necessary
                allowed_user_ids = {getattr(x, 'user_id', 0) for x in self._rows_orm}
                all_user_rows = [row for row in all_user_rows if row.user_id in allowed_user_ids]
            select__api_users = [SelectOption(name=f"{row.user_id}: {row.user_name}", value=row.user_id) for row in all_user_rows]
            if 'select_default' in user_opts:
                self._qc['user_id'].select = select__api_users
                self._qc['user_id'].default = select__api_users[0].value if select__api_users else 1
            if 'add_values' in user_opts:
                self._to.add_values['user_id_name'] = {api_user.value:api_user.name for api_user in select__api_users}
        if group_opts := self.qc_to_user_group.get('group_id', ()):
            # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
            all_group_rows = await ApiGroupsTable(self.session).get_all_not_deleted()            
            if 'allow_all' not in group_opts:  # restrict to fetched if necessary
                allowed_group_ids = {getattr(x, 'group_id', 0) for x in self._rows_orm}
                all_user_rows = [row for row in all_group_rows if row.group_id in allowed_group_ids]
            select__api_groups = [SelectOption(name=f"{row.group_id}: {row.group_name}", value=row.group_id) for row in all_group_rows]            
            if 'select_default' in group_opts:
                self._qc['group_id'].select = select__api_groups
                self._qc['group_id'].default = select__api_groups[0].value if select__api_groups else 1
            if 'add_values' in group_opts:
                self._to.add_values['group_id_name'] = {api_group.value:api_group.name for api_group in select__api_groups}
    
    async def _get_rows_orm(self):
        result = await self.session.execute(self._stmt)
        self._rows_orm = result.scalars().all()

    def _get_rows_pydantic(self):
        self._rows_pydantic = [self.read_model.model_validate(row, from_attributes=True) for row in self._rows_orm]

    async def query(self) -> TableQueryResult[RowModel]:
        self._add_where_clause()
        self._get_order_clause_by_dir()
        await self._get_total()
        if not self._total:
            return TableQueryResult[RowModel](
            name=self.name,
            rows=[],
            columns=self.query_columns,
            table_options=self.table_options,
            order_by=self._order_by,
            order_dir=self._order_dir,
            total=0
        )
        self._add_order_by()
        self._add_limit_offset()
        await self._get_rows_orm()
        await self._update_to_qc()
        self._get_rows_pydantic()        

        return TableQueryResult[RowModel](
            name=self.name,
            rows=self._rows_pydantic,
            columns=self._qc,
            table_options=self._to,
            order_by=self._order_by,
            order_dir=self._order_dir,
            offset=self._offset,
            limit=self._limit,
            total=self._total
        )