from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableCreateRowResult, TableUpdateRowResult
from cwa_lib.pydantic_schemas.su_manage_api_settings import (
    SuManageApiSettingsRead, SuManageApiSettingsCreate, SuManageApiSettingsUpdate
)
from cwa_lib.pages import GenericTableRead


su_manage_api_settings__query_columns = {
    'name': ColumnType(display='Name', type='string'),
    'value': ColumnType(display='Value', type='api_settings_value', default=''),
}

su_manage_api_settings__table_options = TableOptions(
    title='Api Settings',
    pk='name',
    read__visible_columns=['name', 'value'],
    create__ask_columns=['name', 'value'],
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

class SuManageApiSettingsTableRead(GenericTableRead):
    sa_model = ApiSettings
    read_model = SuManageApiSettingsRead
    name = 'api_settings'
    query_columns = su_manage_api_settings__query_columns
    table_options = su_manage_api_settings__table_options
    default_order_by = table_options.pk

class SuManageApiSettingsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_one(self, data: SuManageApiSettingsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        new_row = ApiSettings(
            name=data.name,
            value=data.value
        )
        try:
            self.session.add(new_row)
            await self.session.commit()
            return TableCreateRowResult(result='success', total_created=1)
        except Exception:
            await self.session.rollback()
            return TableCreateRowResult(result='error', total_created=0)

    async def update_one(self, data: SuManageApiSettingsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        result = await self.session.execute(select(ApiSettings).where(ApiSettings.name == data.name))
        vdbs_row = result.scalar_one_or_none()
        if not vdbs_row:
            return TableUpdateRowResult(result='error', total_updated=0)
        vdbs_row.value = data.value.strip()
        await self.session.commit()        
        return TableUpdateRowResult(result='success', total_updated=1)
