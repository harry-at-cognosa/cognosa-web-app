import contextlib
from fastapi_users.exceptions import UserAlreadyExists
from common.helpers import utcnow
from common.sql_db_async import async_get_session, async_get_user_db
from cwa_lib.pydantic_schemas.user import UserCreate
from cwa_lib.users import get_user_manager


get_async_session_context = contextlib.asynccontextmanager(async_get_session)
get_user_db_context = contextlib.asynccontextmanager(async_get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

class ApiUsersTable:
    @staticmethod
    async def create_user(
        email: str, 
        password: str, 
        full_name: str, 
        group_id: int = 2,
        is_active: bool = True, 
        is_verified: bool = False, 
        is_groupadmin: bool = False,
        is_superuser: bool = False
        ):
        try:
            async with get_async_session_context() as session:
                async with get_user_db_context(session) as user_db:
                    async with get_user_manager_context(user_db) as user_manager:
                        user = await user_manager.create(
                            UserCreate(
                                email=email, 
                                password=password, 
                                full_name=full_name,
                                group_id=group_id,
                                is_active=is_active,
                                is_verified=is_verified,
                                is_groupadmin=is_groupadmin,
                                is_superuser=is_superuser,
                                created_at=utcnow()
                            )
                        )
                        print(f"User created: {email}")
                        return user
        except UserAlreadyExists:
            raise Exception(f"Error: User {email} already exists")

