from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
from cwa_lib.pydantic_schemas.manage_llms import ManageLLMsQueryResult, ManageLLMsCreate, ManageLLMsUpdate
from cwa_lib.pages.manage_llms import ManageLLMsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__manage_llms = APIRouter()


@router__manage_llms.post("/manage_llms/query", response_model=ManageLLMsQueryResult)
async def manage_llms__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await ManageLLMsTable(session).query_all(payload=payload, deleted=0)
    return result

@router__manage_llms.post("/manage_llms", response_model=TableCreateRowResult)
async def manage_llms__create(
    request: Request,
    payload: ManageLLMsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageLLMsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_llms.put("/manage_llms", response_model=TableUpdateRowResult)
async def manage_llms__update(
    request: Request,
    payload: ManageLLMsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await ManageLLMsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result


@router__manage_llms.delete("/manage_llms/{gllms_id:int}", response_model=TableDeleteRowResult)
async def manage_llms__delete(
    request: Request,
    gllms_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await ManageLLMsTable(session).mark_deleted_by_gllms_id(gllms_id=gllms_id)
    await log_table.write_result(result)
    return result
