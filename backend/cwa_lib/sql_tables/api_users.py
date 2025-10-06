import contextlib
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select
from common.helpers import utcnow
from common.sql_db_async import async_get_session, async_get_user_db, AsyncSession
from common.sql_models import create_order_clause, User
from common.sql_models.api_users import User
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery
from cwa_lib.pydantic_schemas.manage_users import ManageUsersQueryResult
from cwa_lib.pydantic_schemas.user import UserCreate
from cwa_lib.users import get_user_manager


manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', seqn=1, type='number'), 
    'group_id': ColumnType(display='GroupID', seqn=2, type='number'),
    'user_name': ColumnType(display='User name', seqn=3, type='string'),
    'full_name': ColumnType(display='Full name', seqn=4, type='string'),
    'email': ColumnType(display='Email', seqn=4, type='string'),
    'is_active': ColumnType(display='Active', seqn=5, type='bool_green'),
    'is_contentmanager': ColumnType(display='Content\nManager', seqn=6, type='bool_green'),
    'is_groupadmin': ColumnType(display='Group\nAdmin', seqn=7, type='bool_green'),
    'is_superuser': ColumnType(display='Super\nUser', seqn=8, type='bool_green'),
    'created_at': ColumnType(display='Created at', seqn=9, type='datetime'),
}

manage_users__table_options = TableOptions(
    title='Manage Users',
    pk='user_id',
    allow_add=True,
    allow_update=True,
    allow_delete=True,
    allow_order_by=list(manage_users__query_columns.keys())  # allow order by all
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



get_async_session_context = contextlib.asynccontextmanager(async_get_session)
get_user_db_context = contextlib.asynccontextmanager(async_get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

class ApiUsersTable:
    @staticmethod
    async def async_select_by_user_name(session: AsyncSession, user_name: str) -> User | None:
        stmt = select(User).where(User.user_name == user_name)
        result = await session.scalar(stmt)
        return result

    @staticmethod
    async def create_user(
        user_id: int | None,
        email: str, 
        password: str, 
        user_name: str,
        full_name: str, 
        group_id: int = 2,
        is_active: bool = True, 
        is_verified: bool = False, 
        is_groupadmin: bool = False,
        is_contentmanager: bool = False,
        is_superuser: bool = False
        ):
        try:
            async with get_async_session_context() as session:
                async with get_user_db_context(session) as user_db:
                    async with get_user_manager_context(user_db) as user_manager:
                        user = await user_manager.create(
                            UserCreate(
                                user_id=user_id,
                                email=email, 
                                password=password, 
                                user_name=user_name,
                                full_name=full_name,
                                group_id=group_id,
                                is_active=is_active,
                                is_verified=is_verified,
                                is_groupadmin=is_groupadmin,
                                is_contentmanager=is_contentmanager,
                                is_superuser=is_superuser,
                                created_at=utcnow()
                            )
                        )
                        print(f"User created: {email}")
                        return user
        except UserAlreadyExists:
            raise Exception(f"Error: User {email} already exists")

