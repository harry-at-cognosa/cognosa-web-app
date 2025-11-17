from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import DocTasks
from sqlalchemy import delete
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.su_manage_doc_tasks import SuManageDocTaskRead
from cwa_lib.pages import GenericTableRead

su_manage_doc_tasks__query_columns = {
    'doc_task_id': ColumnType(display='ID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name'),
    'user_id': ColumnType(display='User ID: Name', type='user_id_name'),
    'status': ColumnType(display='', type='number'),
    'status_text': ColumnType(display='', type='text'),
    'short_name': ColumnType(display='', type='text'),
    'input_text': ColumnType(display='', type='text'),
    'optional_text': ColumnType(display='', type='text'),
    'gvdbs_id': ColumnType(display='', type='number'),
    'gvdbs_cfg_json': ColumnType(display='', type='text', min_width='20ch'),
    'gvdbs_json': ColumnType(display='', type='text', min_width='20ch'),
    'gllms_id': ColumnType(display='', type='number'),
    'gllms_json': ColumnType(display='', type='text', min_width='20ch'),
    'gc_id': ColumnType(display='', type='number'),
    'context_json': ColumnType(display='', type='text', min_width='20ch'),
    'sent_to_llm': ColumnType(display='', type='text', min_width='20ch'),
    'output_text': ColumnType(display='', type='text', min_width='20ch'),
    'question_number': ColumnType(display='', type='number'),
    'output_text_2': ColumnType(display='', type='text', min_width='20ch'),
    'exc_text': ColumnType(display='', type='text'),
    'created_at': ColumnType(display='', type='datetime'),
    'fetched_at': ColumnType(display='', type='datetime'),
    'completed_at': ColumnType(display='', type='datetime'),
    'vdb_query_seconds': ColumnType(display='', type='number'),
    'llm_query_seconds': ColumnType(display='', type='number'),
    'llm_tokens_sent': ColumnType(display='', type='number'),
    'llm_tokens_received': ColumnType(display='', type='number'),    
}

su_manage_doc_tasks__all_columns = list(su_manage_doc_tasks__query_columns.keys())

su_manage_doc_tasks__table_options = TableOptions(
    title='Doc Tasks',
    pk='doc_task_id',
    read__visible_columns=su_manage_doc_tasks__all_columns,
    delete__ask_columns=['doc_task_id', 'short_name'],
    order_by__allow=['doc_task_id', 'group_id', 'user_id', 'status', 'created_at'],
    default_limit=5,
    export=['xlsx-current']
)

class SuManageDocTasksTableRead(GenericTableRead):
    sa_model = DocTasks
    read_model = SuManageDocTaskRead
    name = 'su_manage_doc_tasks'
    query_columns = su_manage_doc_tasks__query_columns
    table_options = su_manage_doc_tasks__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'user_id': ('add_values', 'select_default', 'allow_all'), 'group_id': ('add_values', 'select_default', 'allow_all')}

    def _get_where_clause(self):
        where_clause = DocTasks.doc_task_id > -1
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= DocTasks.deleted == deleted
        return where_clause


class SuManageDocTasksTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def delete_by_doc_task_id(self, doc_task_id: int) -> TableDeleteRowResult:
        """
        Delete one by doc_task_id
        """
        where_clause = (DocTasks.doc_task_id == doc_task_id)
        try:
            result = await self.session.execute(delete(DocTasks).where(where_clause))
            return TableDeleteRowResult(result='success', total_deleted=result.rowcount)
        except Exception as exc:
            log.error(f"Exception in SuManageDocTasksTable.delete_by_doc_task_id ({doc_task_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
