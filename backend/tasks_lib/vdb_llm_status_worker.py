from threading import Thread
from time import time, sleep
from common.watchdogs import AP_SLEEP_TIME
from common.sql_db_sync import SqlSyncSession, Session
from common.sql_models import GroupVDBs, GroupLLMs
from tasks_lib.cmd_line_opts import AP_NAME
from tasks_lib.vdb_lib.vdb_ops import VectorDBOps
from tasks_lib.llm_lib.llm_ops import LLMOps
from common.watchdogs.api_processes_table import ApiProcessesTable
from common.watchdogs.group_vdbs import GroupVDBSTable
from common.watchdogs.group_llms import GroupLLMsTable


class VDBLLMStatusWorker(Thread):
    def __init__(self):
        super().__init__()
        self._is_running = False
        self.last_polling = 0.0
        self.ap_subname = "vdb_llm_checking"

    def stop(self):
        self._is_running = False

    def update_ap_status(self, ap_status: str):
        ApiProcessesTable.upsert_api_process(
            ap_type='run_tasks',
            ap_name=AP_NAME,
            ap_subname=self.ap_subname,
            ap_status=ap_status
        )

    def check_one_vdb(self, session: Session, gvdbs: GroupVDBs):
        """Check one row from group_vdbs table"""
        def set_status(gvdbs_status: str, gvdbs_status_text: str):
            GroupVDBSTable.sync_update_gvdbs_status(session, gvdbs.gvdbs_id, gvdbs_status, gvdbs_status_text)
        # check if URL is specified
        try:
            vdb_ops = VectorDBOps(gvdbs.gvdbs_type, gvdbs.gvdbs_url)            
        except Exception:
            set_status(gvdbs_status='danger', gvdbs_status_text='Wrong server URL')
            return
        if error_msg := vdb_ops.check_url():
            set_status(gvdbs_status='danger', gvdbs_status_text=error_msg)
            return
        if vdb_ops.vdb_type == 'chroma':
            set_status(gvdbs_status='warning', gvdbs_status_text="ChromaDB is not checked due to memory leak")
            return
        result = vdb_ops.collection_exists(gvdbs.gvdbs_collection)
        if result is None:
            set_status(gvdbs_status='danger', gvdbs_status_text='Server not found')
        elif result:
            set_status(gvdbs_status='success', gvdbs_status_text='Ready')
        else:
            set_status(gvdbs_status='danger', gvdbs_status_text='Collection not found')
    
    def check_one_llm(self, session: Session, gllms: GroupLLMs):
        """Check one row from group_vdbs table"""
        def set_status(gllms_status: str, gllms_status_text: str):
            GroupLLMsTable.sync_update_gllms_status(session, gllms.gllms_id, gllms_status, gllms_status_text)
        # check if URL is specified
        try:
            llm_ops = LLMOps('', '', '', '', gllms.gllms_type, gllms.gllms_api_base, gllms.gllms_model, gllms.gllms_api_key)
        except Exception:
            set_status(gllms_status='danger', gllms_status_text='Wrong server URL')
            return
        if not llm_ops.check_working():
            set_status(gllms_status='danger', gllms_status_text='LLM server not found')
            return
        set_status(gllms_status='success', gllms_status_text='Ready')

    def check_all(self):
        with SqlSyncSession() as session:
            gvdbs_rows = GroupVDBSTable.sync_select_all(session)
            for gvdbs in gvdbs_rows:
                self.check_one_vdb(session, gvdbs)
            gllms_rows = GroupLLMsTable.sync_select_all(session)
            for gllms in gllms_rows:
                self.check_one_llm(session, gllms)

    def sleep(self):
        """ sleep for the left time until the next polling """
        to_sleep = max(0.0, (self.last_polling + AP_SLEEP_TIME) - time())
        self.last_polling = time()
        sleep(to_sleep)

    def run(self):
        self._is_running = True
        self.update_ap_status('starting')
        while self._is_running:
            try:
                self.update_ap_status('running')
                self.check_all()
                self.sleep()                
            except (SystemExit, KeyboardInterrupt):
                break
        try:
            self.update_ap_status('exit')
        except Exception:
            pass