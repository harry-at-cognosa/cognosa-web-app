from fastapi import APIRouter, Depends, HTTPException, status
from common.sql_db_async import AsyncSession, async_get_session
from fastapi import Form, Response

from common import http_client
from cwa_lib.sql_tables.api_users import ApiUsersTable


router__login_by_username = APIRouter()

@router__login_by_username.post("/auth/jwt/login_by_username")
async def custom_auth_route(
    # Pydantic can't process x-www-form-urlencoded data, so username/password are here:
    username: str = Form(..., min_length=3, max_length=32),
    password: str = Form(...),
    session: AsyncSession = Depends(async_get_session),
):
    user = await ApiUsersTable.async_select_by_user_name(session, user_name=username)
    if not (user and user.is_active):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    response = await http_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": user.email, "password": password}
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
