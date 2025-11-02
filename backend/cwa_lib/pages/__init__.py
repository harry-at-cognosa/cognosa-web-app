from copy import deepcopy
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions
from cwa_lib.sql_tables.api_groups import ApiGroupsTable, AsyncSession


async def get_qc_to_with_group_id_name(
        session: AsyncSession, 
        query_columns: dict[str, ColumnType], 
        table_options: TableOptions,
    ) -> tuple[dict[str, ColumnType], TableOptions]:
    """
    Make deepcopy of {col_name: ColumnType} and TableOptions.
    Add non-deleted {group id: name, ...} values.
    """
    manage_users__qc = deepcopy(query_columns)
    manage_users__to = deepcopy(table_options)
    # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
    select__api_groups = await ApiGroupsTable(session).get_all_not_deleted_as_select_options()
    manage_users__qc['group_id'].select = select__api_groups
    manage_users__qc['group_id'].default = select__api_groups[0].value if select__api_groups else 1
    manage_users__to.add_values['group_id_name'] = {api_group.value:api_group.name for api_group in select__api_groups}
    return manage_users__qc, manage_users__to
