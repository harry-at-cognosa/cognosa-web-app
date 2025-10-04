import contextlib
from sqlalchemy.exc import IntegrityError
from common.helpers import utcnow
from common.sql_db_async import async_get_session
from common.sql_models import ApiGroups


get_async_session_context = contextlib.asynccontextmanager(async_get_session)


class ApiGroupsTable:
    @staticmethod
    async def create_group(
        full_name: str, 
        group_id: int = 2,
        ):
            async with get_async_session_context() as session:
                try:
                    new_group = ApiGroups(
                         group_id=group_id,
                         full_name=full_name,
                         created_at=utcnow()
                        )
                    session.add(new_group)
                    await session.commit()
                    return new_group
                except IntegrityError:
                    await session.rollback()
                    raise Exception(f"Group with ID {group_id} already exists.")
                except Exception as e:
                    await session.rollback()
                    raise Exception("An error occurred while creating the group.")