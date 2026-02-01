from common.sql_db_async import AsyncSession
from common.sql_models.group_vdbs import GroupVDBs
from common.sql_tools import async_reseqn_by_group_id
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import (ColumnType, TableOptions, TableUpdateRowResult)
from cwa_lib.pages import GenericTableRead
from cwa_lib.pydantic_schemas.ga_manage_vdbs import GaManageVDBsRead, GaManageVDBsUpdate
from cwa_lib.sql_tables.api_groups import ApiGroupsTable

ga_manage_vdbs__query_columns = {
    'gvdbs_id': ColumnType(display='ID', type='number'),
    'enabled': ColumnType(display='Enabled?', type='boolean', default=True),
    'gvdbs_seqn': ColumnType(display='Seqn #', type='number', default=0),
    'gvdbs_name': ColumnType(display='Name', type='string', default="New VDB"),
    'gvdbs_retr_params': ColumnType(display='Retrieval Parameters', type='gvdbs_retr_params', default="{}"),
    'gvdbs_status': ColumnType(display='Status', type='gvdbs_status'),
}
gvdbs_edit_columns = [x for x in ga_manage_vdbs__query_columns.keys() if (x not in ('gvdbs_id', 'gvdbs_status'))]

def must_recheck_status_after_update(col: str, value) -> bool:
    if (col == 'enabled') and value:
        return True
    return False

ga_manage_vdbs__table_options = TableOptions(
    title='Document Collections',
    pk='gvdbs_id',
    read__visible_columns=['gvdbs_id', ] + gvdbs_edit_columns + ['gvdbs_status'],
    update__ask_columns=gvdbs_edit_columns,
    order_by__allow=['gvdbs_id', 'enabled', 'gvdbs_seqn', 'gvdbs_name']
)

class GaManageVDBsTableRead(GenericTableRead):
    sa_model = GroupVDBs
    read_model = GaManageVDBsRead
    name = 'ga_manage_vdbs'
    query_columns = ga_manage_vdbs__query_columns
    table_options = ga_manage_vdbs__table_options
    default_order_by = table_options.pk

    def _get_where_clause(self):
        group_id = int(self.kwargs['cur_group_id'])
        where_clause = GroupVDBs.group_id == group_id
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= GroupVDBs.deleted == deleted
        return where_clause
    
    async def _update_to_qc(self):
        await super()._update_to_qc()
        # for new rows, default `gvdbs_retr_params` will be used from `api_groups`.`gvdbs_retr_params` value
        group_id = int(self.kwargs['cur_group_id'])
        api_group = await ApiGroupsTable(self.session).get_group_by_group_id(group_id)
        if not api_group:
            raise Exception(f'No group found: {group_id=}')
        self._qc['gvdbs_retr_params'].default = api_group.gvdbs_retr_params

class GaManageVDBsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resequence_group_vdbs(self, group_id: int, prioritize_gvdbs_id: int) -> None:
        await async_reseqn_by_group_id(self.session, GroupVDBs, group_id, prioritize_gvdbs_id)

    async def update_one(self, cur_group_id: int, data: GaManageVDBsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        where_clause = (GroupVDBs.gvdbs_id == data.gvdbs_id) & (GroupVDBs.group_id == cur_group_id)
        result = await self.session.execute(select(GroupVDBs).where(where_clause))
        vdbs_row = result.scalar_one_or_none()
        if not vdbs_row:
            return TableUpdateRowResult(result='error', total_updated=0)
        if vdbs_row.group_id != cur_group_id:
            return TableUpdateRowResult(result='error', total_updated=0)
        prev_gvdbs_seqn = vdbs_row.gvdbs_seqn        
        total_updated = 0
        need_recheck = False
        for col in gvdbs_edit_columns:
            value = getattr(data, col, None)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(vdbs_row, col, value)
                total_updated = 1
                need_recheck |= must_recheck_status_after_update(col, value)
        
        if need_recheck:
            vdbs_row.gvdbs_status='danger'
            vdbs_row.gvdbs_status_text='Not checked yet' if vdbs_row.enabled else 'Disabled'
            vdbs_row.gvdbs_status_updated_at = None

        await self.session.commit()
        if data.gvdbs_seqn != prev_gvdbs_seqn:
            await self.resequence_group_vdbs(cur_group_id, prioritize_gvdbs_id=data.gvdbs_id)
        return TableUpdateRowResult(result='success', total_updated=total_updated)
