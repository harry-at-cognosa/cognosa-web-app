from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from common.sql_tools import create_order_clause
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery
from cwa_lib.pydantic_schemas.manage_users import ManageUsersQueryResult


manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', seqn=1, type='number'),
    'group_id': ColumnType(display='GroupID', seqn=2, type='number'),
    'user_name': ColumnType(display='User name', seqn=3, type='string'),
    'full_name': ColumnType(display='Full name', seqn=4, type='string'),
    'email': ColumnType(display='Email', seqn=5, type='string'),
    'is_active': ColumnType(display='Active', seqn=6, type='boolean'),
    'is_contentmanager': ColumnType(display='Content\nManager', seqn=7, type='boolean'),
    'is_groupadmin': ColumnType(display='Group\nAdmin', seqn=8, type='boolean'),
    'is_superuser': ColumnType(display='Super\nUser', seqn=9, type='boolean'),
    'created_at': ColumnType(display='Created at', seqn=10, type='datetime'),
}
manage_users__table_options = TableOptions(
    title='Manage Users',
    pk='user_id',
    create__allow=True,
    read__hide_on_false=['is_active', 'is_contentmanager', 'is_groupadmin', 'is_superuser'],  # table view: hide if false
    update__allow=True,
    delete__allow=True,
    delete__ask_columns=['user_name', 'full_name', 'email'],
    order_by__allow=list(manage_users__query_columns.keys()),  # allow order by all    
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