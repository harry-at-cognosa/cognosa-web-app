from common.enums.api_settings_names import API_SETTINGS_NAMES_LIST
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings
from common.sql_tools import create_order_clause
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery, TableUpdateRowResult
from cwa_lib.pydantic_schemas.su_manage_api_settings import SuManageApiSettingsQueryResult, SuManageApiSettingsUpdate


su_manage_api_settings__query_columns = {
    'name': ColumnType(display='Name', type='string'),
    'value': ColumnType(display='Value', type='api_settings_value', default=''),
}

su_manage_api_settings__table_options = TableOptions(
    title='Api Settings',
    pk='name',
    read__visible_columns=['name', 'value'],
    update__ask_columns=['value', ],
    order_by__allow=['name', 'value'],
    add_values={
        'webapp_main_color_values': [
            "slate", "gray", "zinc", "neutral", "stone", "red", "orange", 
            "amber", "yellow", "lime", "green", "emerald", "teal", "cyan",
            "sky", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose"
        ]
    }
)


class SuManageApiSettingsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            payload: TableQuery,
            ) -> SuManageApiSettingsQueryResult:
        
        order_clause, order_by, order_dir = create_order_clause(ApiSettings, 'name', payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(ApiSettings)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return SuManageApiSettingsQueryResult(
            name='manage_vdbs',
            rows=rows,
            columns=su_manage_api_settings__query_columns,
            table_options=su_manage_api_settings__table_options,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def update_one(self, data: SuManageApiSettingsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        name = data.name
        if name not in API_SETTINGS_NAMES_LIST:
            raise Exception(f"Wrong {name=}")
        result = await self.session.execute(select(ApiSettings).where(ApiSettings.name == name))
        vdbs_row = result.scalar_one_or_none()
        if not vdbs_row:
            return TableUpdateRowResult(result='error', total_updated=0)
        vdbs_row.value = data.value.strip()
        await self.session.commit()        
        return TableUpdateRowResult(result='success', total_updated=1)
