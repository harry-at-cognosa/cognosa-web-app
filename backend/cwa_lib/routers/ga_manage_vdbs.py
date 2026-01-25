from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.ga_manage_vdbs import GaManageVDBsQueryResult, GaManageVDBsCreate, GaManageVDBsUpdate
from cwa_lib.pages.ga_manage_vdbs import GaManageVDBsTableRead, GaManageVDBsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__ga_manage_vdbs = APIRouter()


@router__ga_manage_vdbs.post("/groupadmin/manage_vdbs/query", response_model=GaManageVDBsQueryResult)
async def ga_manage_vdbs__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    result = await GaManageVDBsTableRead(session, payload, 
        deleted=0, 
        cur_group_id=user.group_id
    ).query()
    return result

@router__ga_manage_vdbs.post("/groupadmin/manage_vdbs", response_model=TableCreateRowResult)
async def ga_manage_vdbs__create(
    request: Request,
    payload: GaManageVDBsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await GaManageVDBsTable(session).create_one(
        cur_group_id=user.group_id, 
        data=payload
    )
    await log_table.write_result(result)
    return result


@router__ga_manage_vdbs.put("/groupadmin/manage_vdbs", response_model=TableUpdateRowResult)
async def ga_manage_vdbs__update(
    request: Request,
    payload: GaManageVDBsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await GaManageVDBsTable(session).update_one(
        cur_group_id=user.group_id, 
        data=payload
    )
    await log_table.write_result(result)
    return result


@router__ga_manage_vdbs.delete("/groupadmin/manage_vdbs/{gvdbs_id:int}", response_model=TableDeleteRowResult)
async def ga_manage_vdbs__delete(
    request: Request,
    gvdbs_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await GaManageVDBsTable(session).mark_deleted_by_gvdbs_id(
        cur_group_id=user.group_id, 
        gvdbs_id=gvdbs_id
    )
    await log_table.write_result(result)
    return result
