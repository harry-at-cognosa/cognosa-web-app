from time import time
from traceback import format_exc
from common import log
from common.watchdogs.group_vdbs import GroupVDBSTable
from common.watchdogs.group_llms import GroupLLMsTable
from common.sql_db_async import AsyncSession
from cwa_lib.sql_tables.api_settings import ApiSettingsTable

class ServerStatusPage:
    def __init__(self, session: AsyncSession, group_id: int) -> None:
        self.session = session
        self.group_id = group_id

    async def get_api_settings_data(self) -> dict[str, str]:
        return await ApiSettingsTable(self.session).select_by_names(['app_version', 'db_version'])

    async def get_group_vdbs_data(self) -> list[dict]:
        """
        Make group_vdbs data list:
        [
            {
                'gvdbs_name': <string>,
                'gvdbs_status': 'success' / 'warning' / 'danger',
                'gvdbs_status_text': <string>
            }, ...
        ]
        """
        result_list = []
        gvdbs_rows = await GroupVDBSTable.async_select_by_group_id_order_by_seqn(self.session, self.group_id)
        for row in gvdbs_rows:
            status_text = row.gvdbs_status_text if row.gvdbs_status_text else ''
            if not row.gvdbs_status_updated_at:
                status_text = '[Not updated] ' + status_text
            # check if outdated: updated > 2 minutes before
            elif row.gvdbs_status_updated_at.timestamp() < (time() - 120):
                status_text = '[Outdated] ' + status_text
            result_list.append({
                'gvdbs_name': row.gvdbs_name,
                'gvdbs_status': row.gvdbs_status,
                'gvdbs_status_text': status_text,
            })
        return result_list
    
    async def get_group_llms_data(self) -> list[dict]:
        """
        Make group_llms data list:
        [
            {
                'gllms_name': <string>,
                'gllms_status': 'success' / 'warning' / 'danger',
                'gllms_status_text': <string>
            }, ...
        ]
        """
        result_list = []
        gllms_rows = await GroupLLMsTable.async_select_by_group_id_order_by_seqn(self.session, self.group_id)
        for row in gllms_rows:
            status_text = row.gllms_status_text if row.gllms_status_text else ''
            if not row.gllms_status_updated_at:
                status_text = '[Not updated] ' + status_text
            # check if outdated: updated > 2 minutes before
            elif row.gllms_status_updated_at.timestamp() < (time() - 120):
                status_text = '[Outdated] ' + status_text
            result_list.append({
                'gllms_name': row.gllms_name,
                'gllms_status': row.gllms_status,
                'gllms_status_text': status_text,
            })
        return result_list

    async def get_all_data(self) -> dict:
        """
        Make status dict e.g.: 
        {
            'api_settings': 
            {
                'app_version': ...,
                'db_version': ...,
            }
            'group_vdbs_rows': [
                {
                    'gvdbs_name': <string>,
                    'gvdbs_status': 'success' / 'warning' / 'danger',
                    'gvdbs_status_text': <string>
                }, ...
            ],
            'group_llms_rows': [
                {
                    'gllms_name': <string>,
                    'gllms_status': 'success' / 'warning' / 'danger',
                    'gllms_status_text': <string>
                }, ...
            ]
        }        
        """
        try:
            result_dict = {
                'api_settings': await self.get_api_settings_data(),
                'group_vdbs_rows': await self.get_group_vdbs_data(),
                'group_llms_rows': await self.get_group_llms_data(),
            }
        except Exception as exc:
            log.error(f"Error in ServerStatusPage.get_all_data:\n{exc}")
            log.debug(f"Error in ServerStatusPage.get_all_data:\n{format_exc}")
            return dict()
        return result_dict
