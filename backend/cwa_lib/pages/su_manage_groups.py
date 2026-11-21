from common import log
from common.sql_db_async import AsyncSession
from fastapi.exceptions import RequestValidationError
from common.sql_models import ApiGroups, GroupLLMs
from common.sql_tools import fix_autoincrement
from sqlalchemy import select, update
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.su_manage_groups import SuManageGroupsRead, SuManageGroupsCreate, SuManageGroupsUpdate
from cwa_lib.pages import GenericTableRead
from cwa_lib.sql_tables.api_settings import ApiSettingsTable


su_manage_groups__query_columns = {
    'group_id': ColumnType(display='ID', type='number'),
    'group_name': ColumnType(display='Name', type='string', default="New group"),
    'gvdbs_retr_params': ColumnType(display='Retrieval Parameters', type='gvdbs_retr_params', default="{}"),
    'chat_enabled': ColumnType(
        display='Chat?', type='boolean', default=False,
        cu_edit_msg="Whether users of this group see and can use the Chat page."),
    'chat_rewrite_gllms_id': ColumnType(
        display='Chat rewrite LLM ID', type='number', default=None,
        cu_edit_msg="Optional. ID of one of this group's LLMs (see SuperUser / LLMs), used to restate "
                    "follow-up questions before searching. Leave empty to use the LLM of the conversation."),
}

su_manage_groups__table_options = TableOptions(
    title='Manage Groups',
    pk='group_id',
    read__visible_columns=['group_id', 'group_name', 'gvdbs_retr_params', 'chat_enabled', 'chat_rewrite_gllms_id'],
    create__ask_columns=['group_name', 'gvdbs_retr_params', 'chat_enabled'],
    update__ask_columns=['group_name', 'gvdbs_retr_params', 'chat_enabled', 'chat_rewrite_gllms_id'],
    delete__ask_columns=['group_id', 'group_name', 'gvdbs_retr_params'],
    read__hide_on_false=['chat_enabled'],
    order_by__allow=['group_id', 'group_name'],
)

class SuManageGroupsTableRead(GenericTableRead):
    sa_model = ApiGroups
    read_model = SuManageGroupsRead
    name = 'manage_groups'
    query_columns = su_manage_groups__query_columns
    table_options = su_manage_groups__table_options
    default_order_by = table_options.pk

    def _get_where_clause(self):
        where_clause = ApiGroups.group_id > -1
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= ApiGroups.deleted == deleted
        return where_clause
    
    async def _update_to_qc(self):
        await super()._update_to_qc()
        # for new rows, default `gvdbs_retr_params` will be used from `api_settings` -> 'gvdbs_def_retr_params' value
        self._qc['gvdbs_retr_params'].default = await ApiSettingsTable(self.session).select_one('gvdbs_def_retr_params')


class SuManageGroupsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_one(self, data: SuManageGroupsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, ApiGroups)
        group_name__default = su_manage_groups__query_columns['group_name'].default
        new_row = ApiGroups(
            group_name=data.group_name if data.group_name else group_name__default,
            gvdbs_retr_params=data.gvdbs_retr_params,
            chat_enabled=bool(data.chat_enabled),
        )
        self.session.add(new_row)
        await self.session.commit()        
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, data: SuManageGroupsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        update_values = dict()
        if data.group_name:
            update_values['group_name'] = data.group_name.strip()
        if data.gvdbs_retr_params:
            update_values['gvdbs_retr_params'] = data.gvdbs_retr_params.strip()
        if data.chat_enabled is not None:
            update_values['chat_enabled'] = data.chat_enabled
        if 'chat_rewrite_gllms_id' in data.model_fields_set:
            gllms_id = data.chat_rewrite_gllms_id or None
            if gllms_id is not None:
                # must be an LLM of this same group
                found = (await self.session.execute(
                    select(GroupLLMs.gllms_id).where(
                        GroupLLMs.gllms_id == gllms_id,
                        GroupLLMs.group_id == data.group_id,
                        GroupLLMs.deleted == 0,
                    ))).scalar_one_or_none()
                if found is None:
                    raise RequestValidationError([{
                        "loc": ("body", "chat_rewrite_gllms_id"),
                        "msg": f"LLM {gllms_id} is not an LLM of this group",
                        "type": "value_error",
                        "input": gllms_id,
                    }])
            update_values['chat_rewrite_gllms_id'] = gllms_id
        
        if not update_values:
            # Nothing to update
            return TableUpdateRowResult(result='success', total_updated=0)

        where_clause = (ApiGroups.group_id == data.group_id)
        stmt = (
            update(ApiGroups)
            .where(where_clause)
            .values(**update_values)
        )
        result = await self.session.execute(stmt)
        total_updated = result.rowcount
        await self.session.commit()
        return TableUpdateRowResult(result='success', total_updated=total_updated)

    
    async def mark_deleted_by_group_id(self, group_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by group_id.
        """
        where_clause = ApiGroups.group_id == group_id
        try:
            result = await self.session.execute(select(ApiGroups).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            await self.session.commit()
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in ManageGroupsTable.delete_by_group_id ({group_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
