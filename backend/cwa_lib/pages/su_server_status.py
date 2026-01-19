import json
from traceback import format_exc
from common import log
from common.watchdogs import get_outdated_status
from common.watchdogs.group_vdbs import GroupVDBSTable
from common.watchdogs.group_llms import GroupLLMsTable
from common.sql_db_async import AsyncSession
from cwa_lib.sql_tables.api_processes import ApiProcessesTable, ApiProcesses
from cwa_lib.sql_tables.api_settings import ApiSettingsTable

class SuServerStatusPage:
    def __init__(self) -> None:
        pass

    @classmethod
    async def get_api_settings_data(cls, session: AsyncSession) -> dict[str, str]:
        return await ApiSettingsTable(session).select_by_names(['app_version', 'db_version'])

    @classmethod
    async def get_run_tasks_data(cls, session: AsyncSession) -> list[dict]:
        """
        Make run_tasks status list of dictionaries e.g.: 
        [
            {
                'name': 'run_tasks_primary',
                'subprocesses': 
                    [
                        {
                            'name': 'watchdog',
                            "status_text": "...",
                            "is_good": "success" / "warning" / "danger"
                        }
                    ],
            }
        ], ...
        """
        result_list = []
        ap_list = await ApiProcessesTable(session).select_all_running()
        type__name__subname__ap: dict[str, dict[str, dict[str, ApiProcesses]]] = dict()
        for ap in ap_list:
            type__name__subname__ap.setdefault(ap.ap_type, dict()).setdefault(ap.ap_name, dict())[ap.ap_subname] = ap
        # check all run_tasks instances
        run_tasks_base_subnames = ['watchdog', 'polling_loop', 'vdb_llm_checking', 'vdb_p_1']
        name__subname__ap = type__name__subname__ap.get('run_tasks', dict())
        run_tasks_instances = ['run_tasks_primary']
        for instance in sorted(name__subname__ap):
            if instance not in run_tasks_instances:
                run_tasks_instances.append(instance)
        # sort: run_tasks_primary, run_tasks_secondary_1, run_tasks_secondary_2, ...
        run_tasks_instances = sorted(run_tasks_instances, 
                                        key=lambda x: int(x.replace('run_tasks_primary', '0').replace('run_tasks_secondary_', '')))
        for instance in run_tasks_instances:
            instance_dict = {'name': instance, 'subprocesses': []}
            result_list.append(instance_dict)
            subname__ap = name__subname__ap.get(instance, dict())
            run_tasks_subnames = run_tasks_base_subnames[:]
            polling_loop = subname__ap.get('polling_loop')
            if polling_loop:
                # check options: {"vdb_workers_num_to_start": 2}
                vdb_workers_num_to_start = 1
                try:
                    polling_loop_json = json.loads(polling_loop.ap_json)
                    vdb_workers_num_to_start = int(polling_loop_json['vdb_workers_num_to_start'])
                except Exception:
                    polling_loop_json = dict()
                for i in range(2, vdb_workers_num_to_start + 1):
                    run_tasks_subnames.append(f'vdb_p_{i}')
            for subname in run_tasks_subnames:
                ap = subname__ap.get(subname)
                if not ap:
                    instance_dict['subprocesses'].append({
                        'name': subname,
                        'status_text': 'Instance is not found',
                        'is_good': 'danger'
                    })
                    continue
                instance_dict['subprocesses'].append({
                    'name': subname,
                    'status_text': ap.ap_status,
                    'is_good': 'success'
                })

        return result_list
    
    @classmethod
    async def get_group_vdbs_data(cls, session: AsyncSession) -> list[dict]:
        """
        Make group_vdbs data list:
        [
            {
                'gvdbs_id': number,
                'group_id': number,
                'gvdbs_seqn': number,
                'gvdbs_type': <string>,
                'gvdbs_name': <string>,
                'gvdbs_url': <string>,
                'gvdbs_collection': <string>,
                'gvdbs_status': 'success' / 'warning' / 'danger',
                'gvdbs_status_text': <string>
            }, ...
        ]
        """
        result_list = []
        gvdbs_rows = await GroupVDBSTable.async_select_all_order_by_group_id_seqn(session)
        for row in gvdbs_rows:
            result_list.append({
                'gvdbs_id': row.gvdbs_id,
                'group_id': row.group_id,
                'gvdbs_seqn': row.gvdbs_seqn,
                'gvdbs_type': row.gvdbs_type,
                'gvdbs_name': row.gvdbs_name,
                'gvdbs_url': row.gvdbs_url,
                'gvdbs_collection': row.gvdbs_collection,
                'gvdbs_status': row.gvdbs_status,
                'gvdbs_status_text': get_outdated_status(row),
            })
        return result_list
    
    @classmethod
    async def get_group_llms_data(cls, session: AsyncSession) -> list[dict]:
        """
        Make group_llms data list:
        [
            {
                'gllms_id': number,
                'group_id': number,
                'gllms_seqn': number,
                'gllms_type': <string>,
                'gllms_name': <string>,
                'gllms_api_base': <string>,                
                'gllms_model': <string>,
                'gllms_status': 'success' / 'warning' / 'danger',
                'gllms_status_text': <string>
            }, ...
        ]
        """
        result_list = []
        gllms_rows = await GroupLLMsTable.async_select_all_order_by_group_id_seqn(session)
        for row in gllms_rows:
            result_list.append({
                'gllms_id': row.gllms_id,
                'group_id': row.group_id,
                'gllms_seqn': row.gllms_seqn,
                'gllms_type': row.gllms_type,
                'gllms_name': row.gllms_name,
                'gllms_api_base': row.gllms_api_base,
                'gllms_model': row.gllms_model,
                'gllms_status': row.gllms_status,
                'gllms_status_text': get_outdated_status(row),
            })
        return result_list

    @classmethod
    async def get_all_data(cls, session: AsyncSession) -> dict:
        """
        Make status dict e.g.: 
        {
            'api_settings': 
            {
                'app_version': ...,
                'db_version': ...,
            }
            'run_tasks':
                [
                    {
                        'name': 'run_tasks_primary',
                        'subprocesses': 
                            [
                                {
                                    'name': 'watchdog',
                                    'status_text': <string>,
                                    'is_good': 'success' / 'warning' / 'danger'
                                }, ...
                            ],
                    }
                ], ...
            'group_vdbs_rows': [
                {
                    'gvdbs_id': number,
                    'group_id': number,
                    'gvdbs_seqn': number,
                    'gvdbs_type': <string>,
                    'gvdbs_name': <string>,
                    'gvdbs_url': <string>,
                    'gvdbs_collection': <string>,
                    'gvdbs_status': 'success' / 'warning' / 'danger',
                    'gvdbs_status_text': <string>
                }, ...
            ],
            'group_llms_rows': [
                {
                    'gllms_id': number,
                    'group_id': number,
                    'gllms_seqn': number,
                    'gllms_type': <string>,
                    'gllms_name': <string>,
                    'gllms_api_base': <string>,                
                    'gllms_model': <string>,
                    'gllms_status': 'success' / 'warning' / 'danger',
                    'gllms_status_text': <string>
                }, ...
            ]
        }        
        """
        try:
            result_dict = {
                'api_settings': await cls.get_api_settings_data(session),
                'run_tasks': await cls.get_run_tasks_data(session),
                'group_vdbs_rows': await cls.get_group_vdbs_data(session),
                'group_llms_rows': await cls.get_group_llms_data(session),
            }
        except Exception as exc:
            log.error(f"Error in ServerStatusPage.get_all_data:\n{exc}")
            log.debug(f"Error in ServerStatusPage.get_all_data:\n{format_exc}")
            return dict()
        return result_dict
