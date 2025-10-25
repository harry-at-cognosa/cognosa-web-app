from fastapi import APIRouter, Depends, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery
from cwa_lib.pydantic_schemas.su_manage_users import SuManageUsersQueryResult
from cwa_lib.pages.su_manage_users import SuManageUsersTable

router__su_manage_users = APIRouter()


@router__su_manage_users.post("/su/manage_users/query", response_model=SuManageUsersQueryResult)
async def su_manage_users__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(404)

    result = await SuManageUsersTable(session).query_all(
        payload=payload
    )
    return result
