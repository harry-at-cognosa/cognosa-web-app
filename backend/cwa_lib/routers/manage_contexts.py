from fastapi import APIRouter, Depends, Request
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableDeleteRowResult
from cwa_lib.pydantic_schemas.manage_contexts import ManageContextsQueryResult
from cwa_lib.pages.manage_contexts import ManageContextsTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__manage_contexts = APIRouter()


@router__manage_contexts.post("/manage_contexts/query", tags=["Manage Contexts"], response_model=ManageContextsQueryResult)
async def manage_contexts__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await ManageContextsTable(session).query_all_by_group_id(
        group_id=user.group_id, 
        payload=payload,
        deleted=0
    )
    return result

@router__manage_contexts.delete("/manage_contexts/{gc_id}", tags=["Manage Contexts"], response_model=TableDeleteRowResult)
async def manage_contexts__delete(
    request: Request,
    gc_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await ManageContextsTable(session).mark_deleted_by_group_id_gc_id(
        group_id=None if user.is_superuser else user.group_id, 
        gc_id=gc_id
    )
    await log_table.write_result(result)
    return result
