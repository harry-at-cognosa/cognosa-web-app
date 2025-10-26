from fastapi import APIRouter, Depends, HTTPException, Request
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.ga_manage_users import GaManageUsersQueryResult, GaManageUsersCreate, GaManageUsersUpdate
from cwa_lib.pages.ga_manage_users import GaManageUsersTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__ga_manage_users = APIRouter()


@router__ga_manage_users.post("/groupadmin/manage_users/query", response_model=GaManageUsersQueryResult)
async def ga_manage_users__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")

    result = await GaManageUsersTable(session).query_all(
        cur_user_id=user.user_id, 
        cur_group_id=user.group_id, 
        payload=payload
    )
    return result

@router__ga_manage_users.post("/groupadmin/manage_users", response_model=TableCreateRowResult)
async def ga_manage_users__create(
    request: Request,
    payload: GaManageUsersCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await GaManageUsersTable(session).create_one(
        cur_group_id=user.group_id,
        data=payload
    )
    await log_table.write_result(result)
    return result


@router__ga_manage_users.put("/groupadmin/manage_users", response_model=TableUpdateRowResult)
async def ga_manage_users__update(
    request: Request,
    payload: GaManageUsersUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await GaManageUsersTable(session).update_one(
        cur_user_id=user.user_id, 
        cur_group_id=user.group_id, 
        data=payload
    )
    await log_table.write_result(result)
    return result


@router__ga_manage_users.delete("/groupadmin/manage_users/{user_id:int}", response_model=TableDeleteRowResult)
async def ga_manage_users__delete(
    request: Request,
    user_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await GaManageUsersTable(session).mark_deleted_by_user_id(
        cur_user_id=user.user_id, 
        cur_group_id=user.group_id, 
        user_id=user_id
    )
    await log_table.write_result(result)
    return result
