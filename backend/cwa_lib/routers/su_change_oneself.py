from fastapi import APIRouter, Depends, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.su_change_oneself import (
    SuChangeOneselfGetResult, SuChangeOneselfUpdate, SuChangeOneselfUpdateResult
)
from cwa_lib.pages.su_change_oneself import SuChangeOneselfPage

router__su_change_oneself = APIRouter()


@router__su_change_oneself.get("/su/change_oneself", response_model=SuChangeOneselfGetResult)
async def su_change_oneself__get(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404)
    return await SuChangeOneselfPage(session, user).get_options()

@router__su_change_oneself.put("/su/change_oneself", response_model=SuChangeOneselfUpdateResult)
async def su_change_oneself__update(
    payload: SuChangeOneselfUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404)    
    return await SuChangeOneselfPage(session, user).update(payload)
