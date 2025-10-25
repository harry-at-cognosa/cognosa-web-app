from typing import Literal
from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from common.sql_db_async import async_get_session
from common.sql_models import User
from cwa_lib.app import current_active_user
from cwa_lib.sql_tables.api_settings import ApiSettingsTable

class WAOptsApiSettings(BaseModel):
    webapp_main_color: Literal[
        '',
        "slate", "gray", "zinc", "neutral", "stone", "red", "orange", 
        "amber", "yellow", "lime", "green", "emerald", "teal", "cyan",
        "sky", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose"
    ] = ''

class WebAppOptions(BaseModel):
    api_settings: WAOptsApiSettings

router__webapp_options = APIRouter()


@router__webapp_options.get('/webapp_options', tags=["Miscellaneous"])
async def server_status(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
):
    if not user.is_active:
        raise HTTPException(404)
    return {
        'api_settings': await ApiSettingsTable(session).select_by_names(['webapp_main_color',])
    }
