from fastapi import APIRouter, Depends
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.sql_tables.group_contexts import ManageContextsQuery, ManageContextsQueryResult

router__manage_contexts = APIRouter()


@router__manage_contexts.post("/manage_contexts/query", tags=["Manage Contexts"], response_model=ManageContextsQueryResult)
async def manage_contexts__query(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await ManageContextsQuery(session).query_all_by_group_id(group_id=user.group_id)
    return result
