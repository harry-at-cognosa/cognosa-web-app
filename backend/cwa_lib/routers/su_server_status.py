from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from common.sql_db_async import async_get_session
from common.sql_models import User
from cwa_lib.users import current_active_user
from cwa_lib.pages.su_server_status import SuServerStatusPage


router__su_server_status = APIRouter()


@router__su_server_status.get('/su/server_status')
async def server_status(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
):
    if not user.is_superuser:
        raise HTTPException(404)
    return await SuServerStatusPage().get_all_data(session)    
