from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from common.sql_tools import create_order_clause
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery
from cwa_lib.pydantic_schemas.manage_users import ManageUsersQueryResult


manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', type='number'),
    'group_id': ColumnType(display='GroupID', type='number'),
    'user_name': ColumnType(display='User name', type='string'),
    'full_name': ColumnType(display='Full name', type='string'),
    'email': ColumnType(display='Email', type='string'),
    'is_active': ColumnType(display='Active', type='boolean'),
    'is_contentmanager': ColumnType(display='Content\nManager', type='boolean'),
    'is_groupadmin': ColumnType(display='Group\nAdmin', type='boolean'),
    'is_superuser': ColumnType(display='Super\nUser', type='boolean'),
    'created_at': ColumnType(display='Created at', type='datetime'),
}
manage_users__all_columns = list(manage_users__query_columns.keys())

manage_users__table_options = TableOptions(
    title='Manage Users',
    pk='user_id',
    read__visible_columns=manage_users__all_columns,
    read__hide_on_false=['is_active', 'is_contentmanager', 'is_groupadmin', 'is_superuser'],  # table view: hide if false
    delete__ask_columns=['user_name', 'full_name', 'email'],
    order_by__allow=manage_users__all_columns,
)


class ManageUsersTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            payload: TableQuery
            ) -> ManageUsersQueryResult:
        order_clause = create_order_clause(User, manage_users__table_options.pk, payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(User)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return ManageUsersQueryResult(
            name='manage_users',
            rows=rows,
            columns=manage_users__query_columns,
            table_options=manage_users__table_options,
            total=len(rows)
        )