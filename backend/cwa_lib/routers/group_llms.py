from fastapi import APIRouter, Depends
from sqlalchemy import select
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User, GroupLLMs
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.group_llms import GroupLLMsRead


router__group_llms = APIRouter()


# List Group LLMs
@router__group_llms.get("/group_llms", tags=["Group LLMs"], response_model=list[GroupLLMsRead])
async def list_group_llms(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await session.execute(select(GroupLLMs).where(GroupLLMs.group_id == user.group_id))    
    group_contexts = result.scalars().all()
    return group_contexts
