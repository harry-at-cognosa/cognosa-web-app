import multiprocessing
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

import os
from time import time, sleep
from common import log, LOG_SQLALCHEMY_RT
log.init('rt', log_sqlalchemy=LOG_SQLALCHEMY_RT)
if __name__ == "__main__":
    log.info('Starting run_tasks.py...')
from common.sql_db_sync import wait_for_database
wait_for_database()

from common.helpers import start_main
from common.sql_db_sync import get_engine_sessionmaker
from tasks_lib.cmd_line_opts import AP_NAME, IS_PRIMARY_INSTANCE
from tasks_lib.entities.task_queue_msg import VDBTaskExitMsg
from tasks_lib.main_iteration import MainIteration
from tasks_lib.vdb_lib.workers import AllVDBWorkers
from common.watchdogs import AP_SLEEP_TIME, check_name_is_still_running
from common.watchdogs.api_processes_table import ApiProcessesTable
from common.watchdogs.watchdog_thread import WatchdogThread
from tasks_lib.vdb_llm_status_worker import VDBLLMStatusWorker


class RunTasks():
    def __init__(self) -> None:
        self.engine, self.sessionmaker = get_engine_sessionmaker()
        with self.sessionmaker() as session:
            check_name_is_still_running(session, ap_name=AP_NAME)
        self.all_vdb_workers = AllVDBWorkers()
        self.watchdog_thread = WatchdogThread(ap_type='run_tasks', ap_name=AP_NAME)
        self.watchdog_thread.start()
        if IS_PRIMARY_INSTANCE:
            self.vdb_llm_status_worker = VDBLLMStatusWorker()
            self.vdb_llm_status_worker.start()
        self.polling_last_updated = 0.0

    def update_polling_loop_status(self, ap_status: str, ap_dict: dict | None = None, check_time: bool = True):
        cur_time = time()
        if check_time and (cur_time < (self.polling_last_updated + AP_SLEEP_TIME)):
            return
        with self.sessionmaker() as session:
            ApiProcessesTable(session).upsert_api_process(
                ap_type='run_tasks', 
                ap_name=AP_NAME, 
                ap_subname='polling_loop', 
                ap_status=ap_status, 
                ap_json=ap_dict
            )
        self.polling_last_updated = cur_time
        
    def run(self):
        log.info("Starting task polling loop...")
        self.update_polling_loop_status('starting', check_time=False)
        self.all_vdb_workers.start_all()
        main_iteration = MainIteration(self.engine, all_vdb_workers=self.all_vdb_workers)
        self.update_polling_loop_status(
            ap_status='running', 
            ap_dict={
                'vdb_workers_num_to_start': self.all_vdb_workers.num_to_start
            }, 
            check_time=False)
        try:
            while True:
                self.update_polling_loop_status('running')
                status = main_iteration.process_next_task()
                match status:
                    case main_iteration.STATUS__NOT_FOUND:
                        # task not found. Sleep fast.
                        sleep(0.1)
                    case main_iteration.STATUS__PROCESSED_ONE:
                        # task processed. No sleep.
                        continue
                    case main_iteration.STATUS__SQL_ERROR:
                        # SQL error. Wait for 1 second for less logs.
                        sleep(1)
                    case main_iteration.STATUS__TASK_ERROR:
                        # task error. Sleep fast.
                        sleep(0.1)
                    case main_iteration.STATUS__UNDEFINED_ERROR:
                        # undefined error. Wait for 1 second for less logs.
                        sleep(1)
        except (SystemExit, KeyboardInterrupt):
            try:
                self.update_polling_loop_status('exit', check_time=False)
            except Exception:
                pass

    def on_close(self):
        log.info('stopping...')
        try:
            self.engine.dispose()
        except Exception:
            pass
        try:
            self.watchdog_thread.stop()
        except Exception:
            pass
        if IS_PRIMARY_INSTANCE:
            try:
                self.vdb_llm_status_worker.stop()
            except Exception:
                pass
        try:
            self.all_vdb_workers.task_queue.put(VDBTaskExitMsg())
        except Exception:
            pass        
        try:
            self.watchdog_thread.join()
        except Exception:
            pass
        if IS_PRIMARY_INSTANCE:
            try:
                self.vdb_llm_status_worker.join()
            except Exception:
                pass


if __name__ == "__main__":
    run_tasks = RunTasks()
    start_main(run_tasks.run, run_tasks.on_close)
