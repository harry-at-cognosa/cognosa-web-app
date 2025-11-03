from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import LogCRUD
from common.sql_tools import create_order_clause
from sqlalchemy import select, delete
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableQuery, TableDeleteRowResult
)
from cwa_lib.pages import get_qc_to_with_user_id_name_group_id_name
from cwa_lib.pydantic_schemas.su_manage_log_crud import SuManageLogCRUDQueryResult

su_manage_log_crud__query_columns = {
    'lc_id': ColumnType(display='ID', type='number'),
    'dt': ColumnType(display='', type='datetime'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name'),
    'user_id': ColumnType(display='User ID: Name', type='user_id_name'),
    'user_name': ColumnType(display='', type='string'),
    'source_addr': ColumnType(display='', type='string'),
    'method': ColumnType(display='', type='string'),
    'dest_addr': ColumnType(display='', type='string'),
    'data': ColumnType(display='', type='text'),
    'result': ColumnType(display='', type='text'),
}

su_manage_log_crud__all_columns = [x for x in su_manage_log_crud__query_columns.keys() if x not in ('user_name', )]

su_manage_log_crud__table_options = TableOptions(
    title='Log CRUD',
    pk='lc_id',
    read__visible_columns=su_manage_log_crud__all_columns,
    delete__ask_columns=['lc_id', ],
    order_by__allow=['lc_id', ]
)


class SuManageLogCRUDTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            payload: TableQuery
            ) -> SuManageLogCRUDQueryResult:
        # get values to make 'User ID: Name', 'Group ID: Name' columns
        manage_log_crud__qc, manage_log_crud__to = await get_qc_to_with_user_id_name_group_id_name(
            self.session, su_manage_log_crud__query_columns, su_manage_log_crud__table_options,
            {'user_id': ('add_values', 'select_default'), 'group_id': ('add_values', 'select_default')}
        )
        #
        order_clause, order_by, order_dir = create_order_clause(
            LogCRUD, manage_log_crud__to.pk, payload.order_by, payload.order_dir
        )
        result = await self.session.execute(
            select(LogCRUD)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return SuManageLogCRUDQueryResult(
            name='su_manage_log_crud',
            rows=rows,
            columns=manage_log_crud__qc,
            table_options=manage_log_crud__to,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def delete_by_lc_id(self, lc_id: int) -> TableDeleteRowResult:
        """
        Delete one by lc_id
        """
        where_clause = (LogCRUD.lc_id == lc_id)
        try:
            result = await self.session.execute(delete(LogCRUD).where(where_clause))
            return TableDeleteRowResult(result='success', total_deleted=result.rowcount)
        except Exception as exc:
            log.error(f"Exception in SuManageLogCRUDTable.delete_by_lc_id ({lc_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
