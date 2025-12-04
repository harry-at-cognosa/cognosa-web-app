from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.su_manage_vdbs import SuManageVDBsQueryResult, SuManageVDBsCreate, SuManageVDBsUpdate
from cwa_lib.pages.su_manage_vdbs import SuManageVDBsTableRead, SuManageVDBsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__su_manage_vdbs = APIRouter()


@router__su_manage_vdbs.post("/su/manage_vdbs/query", response_model=SuManageVDBsQueryResult)
async def su_manage_vdbs__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageVDBsTableRead(session, payload, deleted=0).query()
    return result

@router__su_manage_vdbs.post("/su/manage_vdbs", response_model=TableCreateRowResult)
async def su_manage_vdbs__create(
    request: Request,
    payload: SuManageVDBsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageVDBsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__su_manage_vdbs.put("/su/manage_vdbs", response_model=TableUpdateRowResult)
async def su_manage_vdbs__update(
    request: Request,
    payload: SuManageVDBsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageVDBsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result


@router__su_manage_vdbs.delete("/su/manage_vdbs/{gvdbs_id:int}", response_model=TableDeleteRowResult)
async def su_manage_vdbs__delete(
    request: Request,
    gvdbs_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await SuManageVDBsTable(session).mark_deleted_by_gvdbs_id(gvdbs_id=gvdbs_id)
    await log_table.write_result(result)
    return result
