from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.su_manage_groups import SuManageGroupsQueryResult, SuManageGroupsCreate, SuManageGroupsUpdate
from cwa_lib.pages.su_manage_groups import SuManageGroupsTableRead, SuManageGroupsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__su_manage_groups = APIRouter()


@router__su_manage_groups.post("/su/manage_groups/query", response_model=SuManageGroupsQueryResult)
async def su_manage_groups__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageGroupsTableRead(session, payload, deleted=0).query()
    return result


@router__su_manage_groups.post("/su/manage_groups", response_model=TableCreateRowResult)
async def su_manage_groups__create(
    request: Request,
    payload: SuManageGroupsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageGroupsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__su_manage_groups.put("/su/manage_groups", response_model=TableUpdateRowResult)
async def su_manage_groups__update(
    request: Request,
    payload: SuManageGroupsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageGroupsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result


@router__su_manage_groups.delete("/su/manage_groups/{group_id:int}", response_model=TableDeleteRowResult)
async def su_manage_groups__delete(
    request: Request,
    group_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await SuManageGroupsTable(session).mark_deleted_by_group_id(group_id)
    await log_table.write_result(result)
    return result
