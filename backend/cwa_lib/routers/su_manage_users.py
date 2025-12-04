from fastapi import APIRouter, Depends, HTTPException, Request
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.su_manage_users import SuManageUsersQueryResult, SuManageUsersCreate, SuManageUsersUpdate
from cwa_lib.pages.su_manage_users import SuManageUsersTableRead, SuManageUsersTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__su_manage_users = APIRouter()


@router__su_manage_users.post("/su/manage_users/query", response_model=SuManageUsersQueryResult)
async def su_manage_users__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(404, detail="Not found")

    result = await SuManageUsersTableRead(session, payload, deleted=0).query()
    return result

@router__su_manage_users.post("/su/manage_users", response_model=TableCreateRowResult)
async def su_manage_users__create(
    request: Request,
    payload: SuManageUsersCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageUsersTable(session).create_one(data=payload)
    await log_table.write_result(result)
    return result


@router__su_manage_users.put("/su/manage_users", response_model=TableUpdateRowResult)
async def su_manage_users__update(
    request: Request,
    payload: SuManageUsersUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageUsersTable(session).update_one(
        cur_user_id=user.user_id, 
        data=payload
    )
    await log_table.write_result(result)
    return result


@router__su_manage_users.delete("/su/manage_users/{user_id:int}", response_model=TableDeleteRowResult)
async def su_manage_users__delete(
    request: Request,
    user_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await SuManageUsersTable(session).mark_deleted_by_user_id(
        cur_user_id=user.user_id, 
        user_id=user_id
    )
    await log_table.write_result(result)
    return result
