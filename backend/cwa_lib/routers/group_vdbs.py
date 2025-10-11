from fastapi import APIRouter, Depends
from sqlalchemy import select
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User, GroupVDBs
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.group_vdbs import GroupVDBsRead


router__group_vdbs = APIRouter()


# List Group VDBs
@router__group_vdbs.get("/group_vdbs", tags=["Group VDBs"], response_model=list[GroupVDBsRead])
async def list_group_vdbs(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    where_clause = (GroupVDBs.group_id == user.group_id) & (GroupVDBs.deleted == 0)
    result = await session.execute(select(GroupVDBs).where(where_clause))
    group_contexts = result.scalars().all()
    return group_contexts
