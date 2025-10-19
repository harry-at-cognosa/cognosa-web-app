from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.manage_groups import ManageGroupsQueryResult, ManageGroupsCreate, ManageGroupsUpdate
from cwa_lib.pages.manage_groups import ManageGroupsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__manage_groups = APIRouter()


@router__manage_groups.post("/manage_groups/query", response_model=ManageGroupsQueryResult)
async def manage_groups__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await ManageGroupsTable(session).query_all(payload=payload, deleted=0)
    return result


@router__manage_groups.post("/manage_groups", response_model=TableCreateRowResult)
async def manage_groups__create(
    request: Request,
    payload: ManageGroupsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageGroupsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_groups.put("/manage_groups", response_model=TableUpdateRowResult)
async def manage_groups__update(
    request: Request,
    payload: ManageGroupsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageGroupsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_groups.delete("/manage_groups/{group_id:int}", response_model=TableDeleteRowResult)
async def manage_groups__delete(
    request: Request,
    group_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await ManageGroupsTable(session).mark_deleted_by_group_id(group_id)
    await log_table.write_result(result)
    return result
