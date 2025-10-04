from datetime import timedelta
import json
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert
from common.sql_db_sync import SqlSyncSession
from common.sql_db_async import AsyncSession
from common.sql_models.api_processes import ApiProcesses


class ApiProcessesAlreadyExists(Exception):
    pass


class ApiProcessesTable:
    def __init__(self) -> None:
        pass

    @classmethod
    async def select_all_running(cls, session: AsyncSession) -> list[ApiProcesses]:
        stmt = (
            select(ApiProcesses)
            .where(
                ApiProcesses.ap_updated_at > func.now() - text("interval '10 seconds'"),
                ApiProcesses.ap_status != "exit"
                )
            )
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @classmethod
    def check_exists_running(cls, ap_name: str, max_before: float) -> bool:
        """
        Check if a row exists with given ap_name and ap_subname 
        where ap_updated_at >= now - max_before and ap_status is not "exit".
        """
        # Calculate the threshold timestamp
        cutoff_time = func.now() - timedelta(seconds=max_before)

        # Query for existing row with matching ap_name, ap_subname and ap_updated_at >= cutoff_time
        stmt = \
            select(ApiProcesses.ap_id)\
            .where((ApiProcesses.ap_name == ap_name) 
                   & (ApiProcesses.ap_updated_at >= cutoff_time)
                   & (ApiProcesses.ap_status != 'exit')
                   )\
            .limit(1)
        with SqlSyncSession() as session:
            return bool(session.execute(stmt).scalar_one_or_none())

    @classmethod
    def upsert_api_process(cls, 
                           ap_type: str, 
                           ap_name: str, 
                           ap_subname: str, 
                           ap_status: str | None = None,
                           ap_json: str | dict | None = None,
                           ) -> None:
        """
        Upsert a new row.
        """
        values_dict = {}
        if ap_status is not None:
            values_dict['ap_status'] = ap_status
        if ap_json is not None:
            values_dict['ap_json'] = ap_json if isinstance(ap_json, str) else json.dumps(ap_json)
        with SqlSyncSession() as session:
            stmt = insert(ApiProcesses)\
                .values(
                    ap_type=ap_type,
                    ap_name=ap_name,
                    ap_subname=ap_subname,
                    **values_dict,
                    ap_updated_at=func.now()
                ).on_conflict_do_update(
                    index_elements=['ap_name', 'ap_subname'],
                    set_={
                        **values_dict,
                        'ap_updated_at': func.now(),
                    }
                ).returning(ApiProcesses.ap_id)
            try:
                session.execute(stmt)
                session.commit()                
            except Exception as e:
                raise Exception(f"Failed to upsert api_process: {str(e)}")
