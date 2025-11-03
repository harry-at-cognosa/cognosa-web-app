import contextlib
from typing import Sequence
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select
from common.helpers import utcnow
from common.sql_db_async import async_get_session, async_get_user_db, AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from cwa_lib.pydantic_schemas.generic_table import SelectOption
from cwa_lib.pydantic_schemas.user import UserCreate
from cwa_lib.users import get_user_manager


get_async_session_context = contextlib.asynccontextmanager(async_get_session)
get_user_db_context = contextlib.asynccontextmanager(async_get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

class ApiUsersTable:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def async_select_by_user_name(self, user_name: str) -> User | None:
        stmt = select(User).where(User.user_name == user_name)
        result = await self.session.scalar(stmt)
        return result
    
    async def get_all_not_deleted(self) -> Sequence[User]:
        result = await self.session.execute(select(User).where(User.deleted==0).order_by(User.user_id))
        return result.scalars().all()
    
    async def get_all_not_deleted_as_select_options(self) -> list[SelectOption]:
        """Get e.g. list[SelectOption(name='1: User1', value=1), ...]"""
        return [
            SelectOption(name=f"{api_user.user_id}: {api_user.user_name}", value=api_user.user_id) 
            for api_user in (await self.get_all_not_deleted())
        ]

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

