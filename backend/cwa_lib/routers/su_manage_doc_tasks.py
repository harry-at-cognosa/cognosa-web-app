from fastapi import APIRouter, Depends, Request, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.users import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableDeleteRowResult
from cwa_lib.pydantic_schemas.su_manage_doc_tasks import SuManageDocTasksQueryResult
from cwa_lib.pages.su_manage_doc_tasks import SuManageDocTasksTableRead, SuManageDocTasksTable
from cwa_lib.sql_tables.log_crud import LogCRUDTable

router__su_manage_doc_tasks = APIRouter()


@router__su_manage_doc_tasks.post("/su/manage_doc_tasks/query", response_model=SuManageDocTasksQueryResult)
async def su_manage_doc_tasks__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageDocTasksTableRead(session, payload, deleted=0).query()
    return result

@router__su_manage_doc_tasks.delete("/su/manage_doc_tasks/{doc_task_id:int}", response_model=TableDeleteRowResult)
async def su_manage_doc_tasks__delete(
    request: Request,
    doc_task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    log_table = LogCRUDTable(session)
    await log_table.add_one(user, request)
    result = await SuManageDocTasksTable(session).delete_by_doc_task_id(doc_task_id=doc_task_id)
    await log_table.write_result(result)
    return result
