from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings


class ApiSettingsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def select_by_names(self, name_list: list[str]) -> dict[str, str]:
        if not name_list:
            return {}
        
        query = select(ApiSettings).where(ApiSettings.name.in_(name_list))
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return {row.name: row.value for row in rows}
