from sqlalchemy import select, func, text
from common.sql_db_async import AsyncSession
from common.sql_models.api_processes import ApiProcesses


class ApiProcessesTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def select_all_running(self) -> list[ApiProcesses]:
        stmt = (
            select(ApiProcesses)
            .where(
                ApiProcesses.ap_updated_at > func.now() - text("interval '10 seconds'"),
                ApiProcesses.ap_status != "exit"
                )
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
