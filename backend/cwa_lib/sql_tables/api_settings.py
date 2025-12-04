import json
from sqlalchemy import select
from common.enums.gvdbs_cfg_json import GVDBsCfgJSON
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings
from common.sql_db_sync import get_engine_sessionmaker


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

    @classmethod
    def prepare_default_values_at_start(cls):
        engine, sessionmaker = get_engine_sessionmaker()
        with sessionmaker() as session:
            # prepare 'gvdbs_cfg_json' value
            result = session.execute(select(ApiSettings).where(ApiSettings.name=='gvdbs_cfg_json')).scalar_one_or_none()
            if not result:
                value = json.dumps(GVDBsCfgJSON.from_dict('{}').as_dict(), default=str)
                row = ApiSettings(name='gvdbs_cfg_json', value=value)
                session.add(row)
                session.commit()
        engine.dispose()
