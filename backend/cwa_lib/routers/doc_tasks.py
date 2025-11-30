from fastapi import APIRouter, Depends, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User
from cwa_lib.app import current_active_user
from cwa_lib.pages.query_documents import QueryDocumentsPage, QueryDocumentsOptions
from cwa_lib.pydantic_schemas.doc_tasks import (
    DocTaskCreate, DocTaskQueryResult, DocTaskQueryShort, DocTaskDeleteResult, DocTaskOptionsResult
)
from cwa_lib.sql_tables.doc_tasks import DocTasksTable


router__doc_tasks = APIRouter()

# Create a new Query Documents task
@router__doc_tasks.post("/doc_tasks", tags=["Query Documents tasks"], response_model=DocTaskQueryResult, status_code=201)
async def create_task(
    payload: DocTaskCreate, 
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(async_get_session)
):
    result = await QueryDocumentsPage(session, user).create_task(payload)    
    if isinstance(result, str):
        raise HTTPException(status_code=500, detail=result)
    return result


# Fetch Query Documents task
@router__doc_tasks.get("/doc_tasks/{doc_task_id:int}", tags=["Query Documents tasks"], response_model=DocTaskQueryResult)
async def get_task(
    doc_task_id: int, 
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(async_get_session),
    ):
    task = await DocTasksTable(session).query_one_by_doc_task_id(doc_task_id=doc_task_id)
    if task is None:
        raise HTTPException(status_code=500, detail="DocTask not found")
    # allow tasks only for user's group_id.
    # allow all tasks for superuser
    if (not user.is_superuser) and (task.group_id != user.group_id):
        raise HTTPException(status_code=404)
    if not user.is_superuser:  # hide context_json for non superusers
        task.context_json = None
    return task

# Delete Query Documents task
@router__doc_tasks.delete("/doc_tasks/{doc_task_id}", tags=["Query Documents tasks"], response_model=DocTaskDeleteResult)
async def delete_task(
    doc_task_id: int, 
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(async_get_session),
    ):
    # superuser can delete any doc_tasks row
    # regular group user can delete only from his group
    use_group_id = None if user.is_superuser else user.group_id
    result = await DocTasksTable(session).delete_one_by_doc_task_id_group_id(doc_task_id=doc_task_id, group_id=use_group_id)
    return DocTaskDeleteResult(doc_task_id=doc_task_id, success=result, error_msg="" if result else "DocTask not found")

# Fetch previous Query Documents tasks (for left tab)
@router__doc_tasks.post("/doc_tasks/query_short", tags=["Query Documents tasks"], response_model=DocTaskQueryShort)
async def doc_tasks__query_short(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    result = await DocTasksTable(session).short_query_all_by_group_id_user_id(group_id=user.group_id, user_id=user.user_id)
    return result


# Fetch Query Documents options: LLM, VDB, Contexts
@router__doc_tasks.get("/doc_tasks/options", tags=["Query Documents tasks"], response_model=DocTaskOptionsResult)
async def get_task_options(
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(async_get_session),
    ):
    return await QueryDocumentsOptions(session, user).get_options()
