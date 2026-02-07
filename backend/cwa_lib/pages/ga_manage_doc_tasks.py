import json
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.doc_tasks import DocTasks
from common.enums.doc_task_status import TaskStatus
from common.features.gvdbs_retr_params import GVDBsRetrParams
from sqlalchemy import delete
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.ga_manage_doc_tasks import GaManageDocTaskRead, type_ga_status_str
from cwa_lib.pages import GenericTableRead

ga_manage_doc_tasks__query_columns = {
    'doc_task_id': ColumnType(display='ID', type='number'),
    'user_id': ColumnType(display='User ID: Name', type='user_id_name'),
    'query_info': ColumnType(display='Info', type='ga_manage_doc_tasks__query_info'),
    'input_text': ColumnType(display='Query', type='ga_manage_doc_tasks__text'),
    'optional_text': ColumnType(display='Optional\nInstruction', type='ga_manage_doc_tasks__text'),
    'context_json': ColumnType(display='Found Documents', type='ga_manage_doc_tasks__text'),
    'sent_to_llm': ColumnType(display='LLM Query', type='ga_manage_doc_tasks__text'),
    'output_text': ColumnType(display='Answer', type='ga_manage_doc_tasks__answer', min_width='20%'),
}

ga_manage_doc_tasks__all_columns = list(ga_manage_doc_tasks__query_columns.keys())
ga_manage_doc_tasks__read_columns = [x for x in ga_manage_doc_tasks__all_columns if x not in ['context_json', 'sent_to_llm']]
ga_manage_doc_tasks__export_columns = [
    'doc_task_id', 'user_id_name', 'status_str', 'short_name', 'input_text', 'optional_text', 'gvdbs_name', 'gvdbs_cfg',
    'gllms_name', 'context_json', 'sent_to_llm', 'output_text', 'output_text_2', 'created_at', 
    'vdb_query_seconds', 'llm_query_seconds', 'llm_tokens_sent', 'llm_tokens_received'
]
ga_manage_doc_tasks__export_columns_display = [
    'doc_task_id', 'User ID: Name', 'Status', 'Short Name', 'Query', 'Optional Instruction', 'Collection', 'Search Options',
    'LLM', 'Found Documents', 'LLM Query', 'Answer', 'Answer_2', 'Placed At', 
    'VectorDB time', 'LLM time', 'Tokens Sent', 'Tokens Recv'
]

ga_manage_doc_tasks__table_options = TableOptions(
    title='Manage Queries',
    pk='doc_task_id',
    read__visible_columns=ga_manage_doc_tasks__read_columns,
    view__visible_columns=ga_manage_doc_tasks__all_columns,
    delete__ask_columns=['doc_task_id', 'query_info'],
    order_by__allow=['doc_task_id', 'user_id'],
    default_limit=10,
    export=['xlsx-current', 'json-current'],
    export_columns=ga_manage_doc_tasks__export_columns,
    export_columns_display=ga_manage_doc_tasks__export_columns_display
)

class GaManageDocTasksTableRead(GenericTableRead):
    sa_model = DocTasks
    read_model = GaManageDocTaskRead
    name = 'ga_manage_doc_tasks'
    query_columns = ga_manage_doc_tasks__query_columns
    table_options = ga_manage_doc_tasks__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'user_id': ('add_values',)}

    def _get_where_clause(self):
        where_clause = DocTasks.group_id == int(self.kwargs['cur_group_id'])
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= DocTasks.deleted == deleted
        return where_clause
    
    def _get_rows_pydantic(self):
        self._rows_orm: list[DocTasks]
        def get_status_str(row: DocTasks) -> type_ga_status_str:
            if row.status in TaskStatus.ERROR_LIST:
                return 'error'
            if row.status in TaskStatus.FINISHED_LIST:
                return 'completed'
            return 'pending'
        def get_gvdbs_name(row: DocTasks) -> str:
            try:
                if row.gvdbs_id == -1:
                    return 'No document search'
                gvdbs_dict = json.loads(row.gvdbs_json)
                return gvdbs_dict['gvdbs_name']
            except Exception:
                return f'N/A (id={row.gvdbs_id})'
        def get_gllms_name(row: DocTasks) -> str:
            try:
                gllms_dict = json.loads(row.gllms_json)
                return gllms_dict['gllms_name']
            except Exception:
                return f'N/A (id={row.gllms_id})'
            
        def get_user_id_name(row: DocTasks) -> str:
            try:
                return self._to.add_values['user_id_name'][row.user_id]
            except Exception:
                return f'N/A (id={row.user_id})'
            
        def get_gvdbs_cfg(row: DocTasks) -> str:
            try:
                if row.gvdbs_id == -1:
                    return ''
                return GVDBsRetrParams.from_str(row.gvdbs_cfg_json).to_short_str()
            except Exception:
                return 'N/A'
        
        self._rows_pydantic = [
            GaManageDocTaskRead(
                doc_task_id=row.doc_task_id,
                user_id=row.user_id,
                user_id_name=get_user_id_name(row),
                status_str=get_status_str(row),
                short_name=row.short_name,
                input_text=row.input_text,
                optional_text=row.optional_text,
                gvdbs_name=get_gvdbs_name(row),
                gvdbs_cfg=row.gvdbs_cfg_json,
                gllms_name=get_gllms_name(row),
                context_json=row.context_json,
                sent_to_llm=row.sent_to_llm,
                output_text=row.output_text,
                question_number=row.question_number,
                output_text_2=row.output_text_2,
                created_at=row.created_at,
                vdb_query_seconds=row.vdb_query_seconds,
                llm_query_seconds=row.llm_query_seconds,
                llm_tokens_sent=row.llm_tokens_sent,
                llm_tokens_received=row.llm_tokens_received
            )
            for row in self._rows_orm
        ]

class GaManageDocTasksTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def delete_by_group_id_doc_task_id(self, group_id: int, doc_task_id: int) -> TableDeleteRowResult:
        """
        Delete one by group_id and doc_task_id
        """
        where_clause = (DocTasks.group_id == group_id) & (DocTasks.doc_task_id == doc_task_id)
        try:
            result = await self.session.execute(delete(DocTasks).where(where_clause))
            return TableDeleteRowResult(result='success', total_deleted=result.rowcount)
        except Exception as exc:
            log.error(f"Exception in GaManageDocTasksTable.delete_by_doc_task_id ({doc_task_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
