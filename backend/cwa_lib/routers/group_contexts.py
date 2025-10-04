from fastapi import APIRouter, Depends
from sqlalchemy import select
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User, GroupContexts
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.group_contexts import GroupContextsRead


router__group_contexts = APIRouter()


# List Group Contexts
@router__group_contexts.get("/group_contexts", tags=["Group Contexts"], response_model=list[GroupContextsRead])
async def list_group_contexts(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await session.execute(select(GroupContexts).where(GroupContexts.group_id == user.group_id))    
    group_contexts = result.scalars().all()
    return group_contexts
