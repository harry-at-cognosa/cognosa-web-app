from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableDeleteRowResult
from cwa_lib.pydantic_schemas.ga_manage_doc_tasks import GaManageDocTasksQueryResult
from cwa_lib.pages.ga_manage_doc_tasks import GaManageDocTasksTableRead, GaManageDocTasksTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__ga_manage_doc_tasks = APIRouter()


@router__ga_manage_doc_tasks.post("/ga/manage_doc_tasks/query", response_model=GaManageDocTasksQueryResult)
async def ga_manage_doc_tasks__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    result = await GaManageDocTasksTableRead(session, payload, deleted=0).query()
    return result

@router__ga_manage_doc_tasks.delete("/ga/manage_doc_tasks/{doc_task_id:int}", response_model=TableDeleteRowResult)
async def ga_manage_doc_tasks__delete(
    request: Request,
    doc_task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_groupadmin:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await GaManageDocTasksTable(session).delete_by_group_id_doc_task_id(
        group_id=user.group_id, 
        doc_task_id=doc_task_id
    )
    await log_table.write_result(result)
    return result
