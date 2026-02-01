from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.group_vdbs import GroupVDBs, GVDBsTypes, GVDBS_TYPE_VALUES
from common.sql_tools import async_reseqn_by_group_id, fix_autoincrement
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import (
    SelectOption, ColumnType, 
    TableOptions, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pages import GenericTableRead
from cwa_lib.pydantic_schemas.su_manage_vdbs import SuManageVDBsRead, SuManageVDBsCreate, SuManageVDBsUpdate
from cwa_lib.sql_tables.api_groups import ApiGroupsTable

select__gvdbs_type = [SelectOption(name=value, value=value) for value in GVDBS_TYPE_VALUES]

su_manage_vdbs__query_columns = {
    'gvdbs_id': ColumnType(display='ID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name', default=1, select=[]),
    'enabled': ColumnType(display='Enabled?', type='boolean', default=True),
    'gvdbs_seqn': ColumnType(display='Seqn #', type='number', default=0),
    'gvdbs_type': ColumnType(display='Type', type='string', default=GVDBsTypes.QDRANT, select=select__gvdbs_type),
    'gvdbs_name': ColumnType(display='Name', type='string', default="New VDB"),
    'gvdbs_url': ColumnType(display='URL', type='string', default="qdrant_local"),
    'gvdbs_collection': ColumnType(display='Collection', type='string', default="New Collection"),
    'gvdbs_retr_params': ColumnType(display='Retrieval Parameters', type='gvdbs_retr_params', default="{}"),
    'gvdbs_retr_filters': ColumnType(display='Retrieval Filters', type='text', default="{}"),
    'gvdbs_status': ColumnType(display='Status', type='gvdbs_status'),
}
gvdbs_edit_columns = [x for x in su_manage_vdbs__query_columns.keys() if (x not in ('gvdbs_id', 'gvdbs_status'))]
gvdbs_create_columns = [x for x in gvdbs_edit_columns if (x not in ('gvdbs_retr_params'))]
gvdbs_order_columns = ['gvdbs_id', 'group_id', 'enabled', 'gvdbs_seqn', 'gvdbs_type', 'gvdbs_name', 'gvdbs_url', 'gvdbs_collection']

su_manage_vdbs__table_options = TableOptions(
    title='Group VDBs',
    pk='gvdbs_id',
    read__visible_columns=['gvdbs_id', ] + gvdbs_edit_columns + ['gvdbs_status'],
    create__ask_columns=gvdbs_create_columns,
    update__ask_columns=gvdbs_edit_columns,
    delete__ask_columns=['gvdbs_id', ] + gvdbs_edit_columns,
    order_by__allow=gvdbs_order_columns
)

class SuManageVDBsTableRead(GenericTableRead):
    sa_model = GroupVDBs
    read_model = SuManageVDBsRead
    name = 'su_manage_vdbs'
    query_columns = su_manage_vdbs__query_columns
    table_options = su_manage_vdbs__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'group_id': ('add_values', 'select_default', 'allow_all')}

    def _get_where_clause(self):
        where_clause = GroupVDBs.gvdbs_id > -1
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= GroupVDBs.deleted == deleted
        return where_clause

class SuManageVDBsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resequence_group_vdbs(self, group_id: int, prioritize_gvdbs_id: int) -> None:
        await async_reseqn_by_group_id(self.session, GroupVDBs, group_id, prioritize_gvdbs_id)

    async def create_one(self, data: SuManageVDBsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, GroupVDBs)
        defaults = {col: su_manage_vdbs__query_columns[col].default 
                    for col in ('gvdbs_seqn', 'gvdbs_name')}
        
        api_group = await ApiGroupsTable(self.session).get_group_by_group_id(data.group_id)
        if not api_group:
            return TableCreateRowResult(result='error', total_created=0, error_msg='No group found')
        
        new_row = GroupVDBs(
            group_id=data.group_id,
            gvdbs_seqn=data.gvdbs_seqn if (data.gvdbs_seqn is not None) else defaults['gvdbs_seqn'],
            gvdbs_type=data.gvdbs_type,
            gvdbs_name=data.gvdbs_name if data.gvdbs_name else defaults['gvdbs_name'],
            gvdbs_url=data.gvdbs_url,
            gvdbs_collection=data.gvdbs_collection,
            gvdbs_emb_model="sentence-transformers/all-MiniLM-L6-v2",
            gvdbs_retr_params=api_group.gvdbs_retr_params,
            gvdbs_status='danger',
            gvdbs_status_text='Not checked yet' if data.enabled else 'Disabled',
        )
        self.session.add(new_row)
        await self.session.commit()
        await self.session.refresh(new_row)
        await self.resequence_group_vdbs(data.group_id, prioritize_gvdbs_id=new_row.gvdbs_id)
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, data: SuManageVDBsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        where_clause = (GroupVDBs.gvdbs_id == data.gvdbs_id)
        result = await self.session.execute(select(GroupVDBs).where(where_clause))
        vdbs_row = result.scalar_one_or_none()
        if not vdbs_row:
            return TableUpdateRowResult(result='error', total_updated=0)
        prev_gvdbs_seqn = vdbs_row.gvdbs_seqn        
        total_updated = 0
        for col in gvdbs_edit_columns:
            value = getattr(data, col, None)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(vdbs_row, col, value)
                total_updated = 1
        
        if total_updated:
            vdbs_row.gvdbs_status='danger'
            vdbs_row.gvdbs_status_text='Not checked yet' if vdbs_row.enabled else 'Disabled'
            vdbs_row.gvdbs_status_updated_at = None

        await self.session.commit()
        await self.session.refresh(vdbs_row)  # to get real group_id
        if data.gvdbs_seqn != prev_gvdbs_seqn:
            await self.resequence_group_vdbs(vdbs_row.group_id, prioritize_gvdbs_id=data.gvdbs_id)
        return TableUpdateRowResult(result='success', total_updated=total_updated)
    
    async def mark_deleted_by_gvdbs_id(self, gvdbs_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by gvdbs_id.
        """
        where_clause = (GroupVDBs.gvdbs_id == gvdbs_id)
        try:
            result = await self.session.execute(select(GroupVDBs).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            await self.session.commit()
            await self.resequence_group_vdbs(row.group_id, prioritize_gvdbs_id=0)
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in SuManageVDBsTable.mark_deleted_by_gvdbs_id ({gvdbs_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
