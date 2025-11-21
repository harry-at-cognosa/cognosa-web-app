from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableCreateRowResult, TableUpdateRowResult
from cwa_lib.pydantic_schemas.su_manage_api_settings import (
    SuManageApiSettingsQueryResult, SuManageApiSettingsCreate, SuManageApiSettingsUpdate
)
from cwa_lib.pages.su_manage_api_settings import SuManageApiSettingsTableRead, SuManageApiSettingsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable
from cwa_lib.validators.api_settings import check_unique__name

router__su_manage_api_settings = APIRouter()


@router__su_manage_api_settings.post("/su/manage_api_settings/query", response_model=SuManageApiSettingsQueryResult)
async def su_manage_api_settings__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageApiSettingsTableRead(session, payload).query()
    return result

@router__su_manage_api_settings.post("/su/manage_api_settings", response_model=TableCreateRowResult)
async def su_manage_llms__create(
    request: Request,
    payload: SuManageApiSettingsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    await check_unique__name(session, payload.name)
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageApiSettingsTable(session).create_one(payload)
    await log_table.write_result(result)
    return result


@router__su_manage_api_settings.put("/su/manage_api_settings", response_model=TableUpdateRowResult)
async def su_manage_api_settings__update(
    request: Request,
    payload: SuManageApiSettingsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request, dict(payload))
    result = await SuManageApiSettingsTable(session).update_one(payload)
    await log_table.write_result(result)
    return result
