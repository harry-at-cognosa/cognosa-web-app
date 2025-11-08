from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import LogCRUD
from sqlalchemy import delete
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableDeleteRowResult
)
from cwa_lib.pages import GenericTableRead
from cwa_lib.pydantic_schemas.su_manage_log_crud import SuManageLogCRUDRead

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

class SuManageLogCRUDTableRead(GenericTableRead):
    sa_model = LogCRUD
    read_model = SuManageLogCRUDRead
    name = 'su_manage_log_crud'
    query_columns = su_manage_log_crud__query_columns
    table_options = su_manage_log_crud__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'user_id': ('add_values', 'select_default', 'allow_all'), 'group_id': ('add_values', 'select_default', 'allow_all')}

    
class SuManageLogCRUDTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
