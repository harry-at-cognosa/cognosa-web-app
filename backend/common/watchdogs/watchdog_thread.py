from threading import Thread
from time import sleep
from .api_processes_table import ApiProcessesTable
from . import AP_SLEEP_TIME


class WatchdogThread(Thread):
    def __init__(self, ap_type: str, ap_name: str, ap_subname: str = 'watchdog'):
        super().__init__()
        self._is_running = False
        self.ap_type = ap_type
        self.ap_name = ap_name
        self.ap_subname = ap_subname        
        self.ap_table = ApiProcessesTable()

    def stop(self):
        self._is_running = False

    def run(self):
        self._is_running = True
        while(self._is_running):
            self.ap_table.upsert_api_process(ap_type='run_tasks', ap_name=self.ap_name, ap_subname=self.ap_subname, ap_status='running')
            sleep(AP_SLEEP_TIME)
        self.ap_table.upsert_api_process(ap_type='run_tasks', ap_name=self.ap_name, ap_subname=self.ap_subname, ap_status='exit')
