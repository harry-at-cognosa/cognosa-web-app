from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import DocTasks
from common.sql_tools import create_order_clause
from sqlalchemy import select, delete
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableQuery, TableDeleteRowResult
)
from cwa_lib.pages import get_qc_to_with_user_id_name_group_id_name
from cwa_lib.pydantic_schemas.su_manage_doc_tasks import SuManageDocTasksQueryResult

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
    'gvdbs_json': ColumnType(display='', type='text'),
    'gllms_id': ColumnType(display='', type='number'),
    'gllms_json': ColumnType(display='', type='text'),
    'gc_id': ColumnType(display='', type='number'),
    'context_json': ColumnType(display='', type='text'),
    'sent_to_llm': ColumnType(display='', type='text'),
    'output_text': ColumnType(display='', type='text'),
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
    order_by__allow=['doc_task_id', 'group_id', 'user_id', 'status', 'created_at']
)


class SuManageDocTasksTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            payload: TableQuery,
            deleted: int | None
            ) -> SuManageDocTasksQueryResult:
        # get values to make 'User ID: Name', 'Group ID: Name' columns
        manage_doc_tasks__qc, manage_doc_tasks__to = await get_qc_to_with_user_id_name_group_id_name(
            self.session, su_manage_doc_tasks__query_columns, su_manage_doc_tasks__table_options,
            {'user_id': ('add_values', 'select_default'), 'group_id': ('add_values', 'select_default')}
        )
        #
        where_clause = DocTasks.doc_task_id > -1
        if deleted is not None:
            where_clause &= DocTasks.deleted == deleted
        order_clause, order_by, order_dir = create_order_clause(
            DocTasks, manage_doc_tasks__to.pk, payload.order_by, payload.order_dir
        )
        result = await self.session.execute(
            select(DocTasks)
            .where(where_clause)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return SuManageDocTasksQueryResult(
            name='su_manage_doc_tasks',
            rows=rows,
            columns=manage_doc_tasks__qc,
            table_options=manage_doc_tasks__to,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
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
