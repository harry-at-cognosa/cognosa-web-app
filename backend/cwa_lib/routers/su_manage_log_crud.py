from fastapi import APIRouter, Depends, HTTPException
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models.api_users import User
from cwa_lib.app import current_active_user
from cwa_lib.pydantic_schemas.generic_table import TableQuery, TableDeleteRowResult
from cwa_lib.pydantic_schemas.su_manage_log_crud import SuManageLogCRUDQueryResult
from cwa_lib.pages.su_manage_log_crud import SuManageLogCRUDTable

router__su_manage_log_crud = APIRouter()


@router__su_manage_log_crud.post("/su/manage_log_crud/query", response_model=SuManageLogCRUDQueryResult)
async def su_manage_log_crud__query(
    payload: TableQuery,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageLogCRUDTable(session).query_all(payload=payload)
    return result

@router__su_manage_log_crud.delete("/su/manage_log_crud/{lc_id:int}", response_model=TableDeleteRowResult)
async def su_manage_log_crud__delete(
    lc_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
    ):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="Not found")
    result = await SuManageLogCRUDTable(session).delete_by_lc_id(lc_id=lc_id)
    return result
