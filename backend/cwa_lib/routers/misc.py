from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.sql_db_async import async_get_session
from common.sql_models import User
from cwa_lib.pydantic_schemas.user import ChangePasswordRequest
from cwa_lib.app import current_active_user, password_helper
from cwa_lib.pages.server_status import ServerStatusPage


router__misc = APIRouter()


@router__misc.get("/hello", tags=["Miscellaneous"])
async def hello(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}"}


@router__misc.post("/change_password", tags=["Miscellaneous"])
async def change_password(
    change_password_request: ChangePasswordRequest,    
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
):
    current_password = change_password_request.current_password
    new_password = change_password_request.new_password
    if not password_helper.verify_and_update(current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

    user.hashed_password = password_helper.hash(new_password)
    await session.commit()
    return {"status": "password updated"}


@router__misc.get('/server_status', tags=["Miscellaneous"])
async def server_status(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
):
    if user.is_superuser:
        return await ServerStatusPage().get_all_data(session)    
    return {}