AP_SLEEP_TIME = 5.0  # sleep time to update api_processes.updated_at
AP_MAX_BEFORE = 10.0  # max before time to check if previous process is running with same api_processes.ap_name

from common import log
from .api_processes_table import ApiProcessesTable, Session

def check_name_is_still_running(session: Session, ap_name: str) -> bool | None:
    if ApiProcessesTable(session).check_exists_running(ap_name, max_before=AP_MAX_BEFORE):
        log.error(f"Process ap_name='{ap_name}' seems to be running in 'api_processes' PostgreSQL table")
        exit(-1)
