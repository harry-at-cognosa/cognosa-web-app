AP_SLEEP_TIME = 5.0  # sleep time to update api_processes.updated_at
AP_MAX_BEFORE = 10.0  # max before time to check if previous process is running with same api_processes.ap_name

from time import time
from common import log
from .api_processes_table import ApiProcessesTable, Session
from common.enums.gllms_types import public_api_gllms_types
from common.sql_models.group_llms import GroupLLMs
from common.sql_models.group_vdbs import GroupVDBs

def check_name_is_still_running(session: Session, ap_name: str) -> bool | None:
    if ApiProcessesTable(session).check_exists_running(ap_name, max_before=AP_MAX_BEFORE):
        log.error(f"Process ap_name='{ap_name}' seems to be running in 'api_processes' PostgreSQL table")
        exit(-1)


def get_outdated_status(row: GroupLLMs | GroupVDBs) -> str:
    """
    Check if `group_llms` or `group_vdbs` row is outdated or not updated.
    Return `status_text` as one of:
        1) status_text
        2) [Outdated] status_text
        3) [Not updated] status_text
    """
    if isinstance(row, GroupLLMs):
        status_text = row.gllms_status_text if row.gllms_status_text else ''
        status_updated_at = row.gllms_status_updated_at
    else:
        status_text = row.gvdbs_status_text if row.gvdbs_status_text else ''
        status_updated_at = row.gvdbs_status_updated_at
    if not status_updated_at:
        status_text = '[Not updated] ' + status_text
    # check if outdated: updated > 10 minutes before
    elif status_updated_at.timestamp() < (time() - 600):
        status_text = '[Outdated] ' + status_text
    return status_text

def is_need_to_check_llm(row: GroupLLMs) -> bool:
    """
    Less checks for public LLM API: only once in 5 minutes.
    """
    if row.gllms_type in public_api_gllms_types:
        if row.gllms_status_updated_at and (row.gllms_status_updated_at.timestamp() > (time() - 300)):
            return False
    return True
