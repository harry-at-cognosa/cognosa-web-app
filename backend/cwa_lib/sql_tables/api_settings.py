from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings


class ApiSettingsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def select_by_names(self, name_list: list[str]) -> dict[str, str]:
        empty_values = {k: '' for k in name_list}
        if not name_list:
            return empty_values
        
        query = select(ApiSettings).where(ApiSettings.name.in_(name_list))
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return {**empty_values, **{row.name: row.value for row in rows}}
