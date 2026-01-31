from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings
# from common.sql_db_sync import get_engine_sessionmaker


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
    
    async def select_one(self, name: str, default: str = '') -> str:
        query = select(ApiSettings).where(ApiSettings.name == name)
        result = await self.session.execute(query)
        if row := result.scalar_one_or_none():
            value = row.value.strip()
            return value if value else default
        return default

    @classmethod
    def prepare_default_values_at_start(cls):
        # engine, sessionmaker = get_engine_sessionmaker()
        # with sessionmaker() as session:
        #     pass
        # engine.dispose()
        pass
