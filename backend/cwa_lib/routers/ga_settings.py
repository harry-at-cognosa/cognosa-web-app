from fastapi import APIRouter, Depends, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.pydantic_schemas.ga_settings import GaGVDBsRetrParamsPut
from cwa_lib.sql_tables.api_groups import ApiGroupsTable
from cwa_lib.users import current_active_user

router__ga_settings = APIRouter()


@router__ga_settings.get("/groupadmin/settings/gvdbs_retr_params")
async def ga_settings__gvdbs_retr_params__get(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    api_groups = await ApiGroupsTable(session).get_group_by_group_id(user.group_id)
    return api_groups.gvdbs_retr_params

@router__ga_settings.put("/groupadmin/settings/gvdbs_retr_params")
async def ga_settings__gvdbs_retr_params__put(
    payload: GaGVDBsRetrParamsPut,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    api_groups = await ApiGroupsTable(session).get_group_by_group_id(user.group_id)
    api_groups.gvdbs_retr_params = payload.gvdbs_retr_params
    await session.commit()
    return api_groups.gvdbs_retr_params
