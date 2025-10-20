from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.manage_vdbs import ManageVDBsQueryResult, ManageVDBsCreate, ManageVDBsUpdate
from cwa_lib.pages.manage_vdbs import ManageVDBsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__manage_vdbs = APIRouter()


@router__manage_vdbs.post("/manage_vdbs/query", response_model=ManageVDBsQueryResult)
async def manage_vdbs__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await ManageVDBsTable(session).query_all(payload=payload, deleted=0)
    return result

@router__manage_vdbs.post("/manage_vdbs", response_model=TableCreateRowResult)
async def manage_vdbs__create(
    request: Request,
    payload: ManageVDBsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageVDBsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_vdbs.put("/manage_vdbs", response_model=TableUpdateRowResult)
async def manage_vdbs__update(
    request: Request,
    payload: ManageVDBsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageVDBsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_vdbs.delete("/manage_vdbs/{gvdbs_id:int}", response_model=TableDeleteRowResult)
async def manage_vdbs__delete(
    request: Request,
    gvdbs_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await ManageVDBsTable(session).mark_deleted_by_gvdbs_id(gvdbs_id=gvdbs_id)
    await log_table.write_result(result)
    return result
