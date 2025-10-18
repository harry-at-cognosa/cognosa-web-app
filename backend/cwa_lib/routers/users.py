from fastapi import APIRouter, Depends, HTTPException, status
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User, ApiGroups
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.user import UsersMe
from cwa_lib.sql_tables.api_groups import ApiGroupsTable

router__users = APIRouter()

# GET /users/me route
@router__users.get("/users/me", tags=["Users"], response_model=UsersMe)
async def users_me(
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(async_get_session)
):
    if not (user and user.is_active):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    group_obj = await ApiGroupsTable(session).get_group_by_group_id(user.group_id)
    return UsersMe(**user.__dict__, group_name=group_obj.group_name)
