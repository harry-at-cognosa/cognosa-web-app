from copy import deepcopy
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions
from cwa_lib.sql_tables.api_users import ApiUsersTable, AsyncSession
from cwa_lib.sql_tables.api_groups import ApiGroupsTable
from typing import Literal

__UserGroupChoose = dict[Literal['user_id', 'group_id'], tuple[Literal['add_values', 'select_default'], ...]]

async def get_qc_to_with_user_id_name_group_id_name(
        session: AsyncSession, 
        query_columns: dict[str, ColumnType], 
        table_options: TableOptions,
        user_group: __UserGroupChoose
    ) -> tuple[dict[str, ColumnType], TableOptions]:
    """
    Make deepcopy of {col_name: ColumnType} and TableOptions.
    Add non-deleted {user id: name, ...} values.
    Add non-deleted {group id: name, ...} values.
    """
    manage_users__qc = deepcopy(query_columns)
    manage_users__to = deepcopy(table_options)
    if user_opts := user_group.get('user_id', ()):
        # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
        select__api_users = await ApiUsersTable(session).get_all_not_deleted_as_select_options()
        if 'select_default' in user_opts:
            manage_users__qc['user_id'].select = select__api_users
            manage_users__qc['user_id'].default = select__api_users[0].value if select__api_users else 1
        if 'add_values' in user_opts:
            manage_users__to.add_values['user_id_name'] = {api_user.value:api_user.name for api_user in select__api_users}
    if group_opts := user_group.get('group_id', ()):
        # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
        select__api_groups = await ApiGroupsTable(session).get_all_not_deleted_as_select_options()
        if 'select_default' in group_opts:
            manage_users__qc['group_id'].select = select__api_groups
            manage_users__qc['group_id'].default = select__api_groups[0].value if select__api_groups else 1
        if 'add_values' in group_opts:
            manage_users__to.add_values['group_id_name'] = {api_group.value:api_group.name for api_group in select__api_groups}
    return manage_users__qc, manage_users__to
