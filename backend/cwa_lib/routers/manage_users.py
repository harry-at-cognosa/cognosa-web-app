from fastapi import APIRouter, Depends
from common.sql_db_async import AsyncSession, async_get_session
from cwa_lib.pydantic_schemas.generic_table import TableQuery
from cwa_lib.pydantic_schemas.manage_users import ManageUsersQueryResult
from cwa_lib.pages.manage_users import ManageUsersTable

router__manage_users = APIRouter()


@router__manage_users.post("/manage_users/query", tags=["Manage Users"], response_model=ManageUsersQueryResult)
async def manage_users__query(
    payload: TableQuery,
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await ManageUsersTable(session).query_all(
        payload=payload
    )
    return result
