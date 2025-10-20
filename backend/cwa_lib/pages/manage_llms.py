from copy import deepcopy
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.group_llms import GroupLLMs, GLLMsTypes, GLLMS_TYPE_VALUES
from common.sql_tools import create_order_clause, async_reseqn_by_group_id, fix_autoincrement
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import (
    SelectOption, ColumnType, 
    TableOptions, TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.manage_llms import ManageLLMsQueryResult, ManageLLMsCreate, ManageLLMsUpdate
from cwa_lib.sql_tables.api_groups import ApiGroupsTable

select__gllms_type = [SelectOption(name=value, value=value) for value in GLLMS_TYPE_VALUES]

manage_llms__query_columns = {
    'gllms_id': ColumnType(display='ID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name', default=1, select=[]),
    'gllms_seqn': ColumnType(display='Seqn #', type='number', default=0),
    'gllms_type': ColumnType(display='Type', type='string', default=GLLMsTypes.OLLAMA_LOCAL, select=select__gllms_type),
    'gllms_name': ColumnType(display='Name', type='string', default="New LLM"),
    'gllms_api_base': ColumnType(display='API Base', type='string', default="http://localhost:11434/v1"),
    'gllms_model': ColumnType(display='Model', type='string', default="gemma3"),
    'gllms_api_key': ColumnType(display='API Key', type='string', default=""),
    'gllms_status': ColumnType(display='Status', type='gllms_status'),
}
gllms_edit_columns = [x for x in manage_llms__query_columns.keys() if (x not in ('gllms_id', 'gllms_status'))]

manage_llms__table_options = TableOptions(
    title='Group LLMs',
    pk='gllms_id',
    read__visible_columns=['gllms_id', ] + gllms_edit_columns + ['gllms_status'],
    create__ask_columns=gllms_edit_columns,
    update__ask_columns=gllms_edit_columns,
    delete__ask_columns=['gllms_id', ] + gllms_edit_columns,
    order_by__allow=['gllms_id', ] + gllms_edit_columns
)


class ManageLLMsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resequence_group_llms(self, group_id: int, prioritize_gllms_id: int) -> None:
        await async_reseqn_by_group_id(self.session, GroupLLMs, group_id, prioritize_gllms_id)

    async def query_all(
            self,
            payload: TableQuery,
            deleted: int | None
            ) -> ManageLLMsQueryResult:
        
        manage_llms__qc = deepcopy(manage_llms__query_columns)
        manage_llms__to = deepcopy(manage_llms__table_options)
        # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
        select__api_groups = await ApiGroupsTable(self.session).get_all_not_deleted_as_select_options()
        manage_llms__qc['group_id'].select = select__api_groups
        manage_llms__qc['group_id'].default = select__api_groups[0].value if select__api_groups else 1
        manage_llms__to.add_values['group_id_name'] = {api_group.value:api_group.name for api_group in select__api_groups}
        #
        where_clause = GroupLLMs.gllms_id > -1
        if deleted is not None:
            where_clause &= GroupLLMs.deleted == deleted
        order_clause, order_by, order_dir = create_order_clause(GroupLLMs, 'gllms_id', payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(GroupLLMs)
            .where(where_clause)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return ManageLLMsQueryResult(
            name='manage_llms',
            rows=rows,
            columns=manage_llms__qc,
            table_options=manage_llms__to,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def create_one(self, data: ManageLLMsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, GroupLLMs)
        defaults = {col: manage_llms__query_columns[col].default 
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
    
    async def update_one(self, data: ManageLLMsUpdate) -> TableUpdateRowResult:
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
