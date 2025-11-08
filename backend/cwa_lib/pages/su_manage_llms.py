from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.group_llms import GroupLLMs, GLLMsTypes, GLLMS_TYPE_VALUES
from common.sql_tools import async_reseqn_by_group_id, fix_autoincrement
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import (
    SelectOption, ColumnType, 
    TableOptions, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pages import GenericTableRead
from cwa_lib.pydantic_schemas.su_manage_llms import SuManageLLMsRead, SuManageLLMsCreate, SuManageLLMsUpdate

select__gllms_type = [SelectOption(name=value, value=value) for value in GLLMS_TYPE_VALUES]

su_manage_llms__query_columns = {
    'gllms_id': ColumnType(display='ID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name', default=1, select=[]),
    'gllms_seqn': ColumnType(display='Seqn #', type='number', default=0),
    'gllms_type': ColumnType(display='Type', type='string', default=GLLMsTypes.OLLAMA_LOCAL, select=select__gllms_type),
    'gllms_name': ColumnType(display='Name', type='string', default="New LLM"),
    'gllms_api_base': ColumnType(display='API Base', type='string', default="ollama_local"),
    'gllms_model': ColumnType(display='Model', type='string', default="gemma3"),
    'gllms_api_key': ColumnType(display='API Key', type='text', default=""),
    'gllms_status': ColumnType(display='Status', type='gllms_status'),
}
gllms_edit_columns = [x for x in su_manage_llms__query_columns.keys() if (x not in ('gllms_id', 'gllms_status'))]

su_manage_llms__table_options = TableOptions(
    title='Group LLMs',
    pk='gllms_id',
    read__visible_columns=['gllms_id', ] + gllms_edit_columns + ['gllms_status'],
    create__ask_columns=gllms_edit_columns,
    update__ask_columns=gllms_edit_columns,
    delete__ask_columns=['gllms_id', ] + gllms_edit_columns,
    order_by__allow=['gllms_id', ] + gllms_edit_columns
)

class SuManageLLMsTableRead(GenericTableRead):
    sa_model = GroupLLMs
    read_model = SuManageLLMsRead
    name = 'manage_llms'
    query_columns = su_manage_llms__query_columns
    table_options = su_manage_llms__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'group_id': ('add_values', 'select_default', 'allow_all')}

    def _get_where_clause(self):
        where_clause = GroupLLMs.gllms_id > -1
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= GroupLLMs.deleted == deleted
        return where_clause

class SuManageLLMsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resequence_group_llms(self, group_id: int, prioritize_gllms_id: int) -> None:
        await async_reseqn_by_group_id(self.session, GroupLLMs, group_id, prioritize_gllms_id)

    async def create_one(self, data: SuManageLLMsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, GroupLLMs)
        defaults = {col: su_manage_llms__query_columns[col].default 
                    for col in ('gllms_seqn', 'gllms_name')}
        
        new_row = GroupLLMs(
            group_id=data.group_id,
            gllms_seqn=data.gllms_seqn if (data.gllms_seqn is not None) else defaults['gllms_seqn'],
            gllms_type=data.gllms_type,
            gllms_name=data.gllms_name if data.gllms_name else defaults['gllms_name'],
            gllms_api_base=data.gllms_api_base,
            gllms_model=data.gllms_model,
            gllms_api_key=data.gllms_api_key,
        )
        self.session.add(new_row)
        await self.session.commit()
        await self.session.refresh(new_row)
        await self.resequence_group_llms(data.group_id, prioritize_gllms_id=new_row.gllms_id)
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, data: SuManageLLMsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        where_clause = (GroupLLMs.gllms_id == data.gllms_id)
        result = await self.session.execute(select(GroupLLMs).where(where_clause))
        llms_row = result.scalar_one_or_none()
        if not llms_row:
            return TableUpdateRowResult(result='error', total_updated=0)
        prev_gllms_seqn = llms_row.gllms_seqn        
        total_updated = 0
        for col in gllms_edit_columns:
            value = getattr(data, col, None)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(llms_row, col, value)
                total_updated = 1
        
        await self.session.commit()
        await self.session.refresh(llms_row)  # to get real group_id
        if data.gllms_seqn != prev_gllms_seqn:
            await self.resequence_group_llms(llms_row.group_id, prioritize_gllms_id=data.gllms_id)
        return TableUpdateRowResult(result='success', total_updated=total_updated)

    
    async def mark_deleted_by_gllms_id(self, gllms_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by gllms_id.
        """
        where_clause = (GroupLLMs.gllms_id == gllms_id)
        try:
            result = await self.session.execute(select(GroupLLMs).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            await self.session.commit()
            await self.resequence_group_llms(row.group_id, prioritize_gllms_id=0)
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in ManageLLMsTable.delete_by_group_id_gllms_id ({gllms_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
