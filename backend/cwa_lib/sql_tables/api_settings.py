import json
from sqlalchemy import select, delete
from common.features.gvdbs_retr_params import DEFAULT_RETR_PARAMS, GVDBsDefRetrParams
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
            ###
            # prepare 'gvdbs_def_retr_params' value
            ###
            result = session.execute(select(ApiSettings).where(ApiSettings.name=='gvdbs_def_retr_params')).scalar_one_or_none()
            if not result:
                # try to convert `api_settings` -> `gvdbs_cfg_json` to new `gvdbs_def_retr_params` or use DEFAULT_RETR_PARAMS
                old_value = session.execute(select(ApiSettings).where(ApiSettings.name=='gvdbs_cfg_json')).scalar_one_or_none()
                if old_value:
                    def_retr_params = GVDBsDefRetrParams.from_obsolete_gvdbs_cfg(old_value.value).as_dict()
                else:
                    def_retr_params = DEFAULT_RETR_PARAMS
                row = ApiSettings(name='gvdbs_def_retr_params', value=json.dumps(def_retr_params, default=str))
                session.add(row)
                # delete old value: api_settings -> gvdbs_cfg_json. TODO: to be removed later.
                if old_value:
                    session.execute(delete(ApiSettings).where(ApiSettings.name=='gvdbs_cfg_json'))
                session.commit()
        engine.dispose()
