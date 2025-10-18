import json
from multiprocessing import Process, Queue, cpu_count
from queue import Empty
from time import time
from traceback import format_exc
from common import log, LOG_SQLALCHEMY_RT, RT_VDB_PROCESS_NUM
from common.helpers import utcnow
from tasks_lib.entities.task_queue_msg import VDBDocTaskQueueMsg, VDBTaskExitMsg
from common.sql_db_sync import SqlSyncSession, Session
from common.sql_models import DocTasks
from common.enums.doc_task_status import TaskStatus
from tasks_lib.vdb_lib.vdb_ops import VectorDBOps
from tasks_lib.vdb_lib.emb_models import EmbModels
from tasks_lib.cmd_line_opts import AP_NAME
from common.watchdogs import AP_SLEEP_TIME
from common.watchdogs.api_processes_table import ApiProcessesTable


class VDBWorker(Process):
    def __init__(self, process_index: int, task_queue: Queue) -> None:
        super().__init__()
        self.process_index = process_index
        self.ap_subname = f'vdb_p_{self.process_index}'
        self.task_queue = task_queue

    def save_error_to_sql(self, session: Session, task: DocTasks, error_msg: str, exc_msg: str | None = None):
        log.info(f"Task id {task.doc_task_id} error")
        exc_msg = exc_msg if exc_msg else error_msg
        task.exc_text = exc_msg[:20000]
        task.status_text = error_msg[:1000]
        task.status = TaskStatus.QD_VDB_ERROR
        session.commit()        

    def save_results_to_sql(self, session: Session, task: DocTasks, result_dict: list[dict], vdb_query_seconds: float):
        doc_number = len(result_dict)
        context_json=json.dumps(result_dict, indent=1)        
        log.info(f"Task id {task.doc_task_id} completed")
        task.context_at = utcnow()
        task.context_json = context_json
        task.status = TaskStatus.QD_VDB_FETCHED
        task.status_text = f"Documents search completed. Found {doc_number} documents. Sending to LLM..."
        task.vdb_query_seconds=vdb_query_seconds
        session.commit()

    def update_ap_status(self, ap_status: str):
        ApiProcessesTable.upsert_api_process(
            ap_type='run_tasks',
            ap_name=AP_NAME,
            ap_subname=self.ap_subname,
            ap_status=ap_status
        )

    def run(self):
        log.init(prefix=f'rt-p{self.process_index}', log_sqlalchemy=LOG_SQLALCHEMY_RT)        
        self.update_ap_status('starting')
        emb_models = EmbModels(preload_emb_models=True)
        log.info(f"VDB Worker {self.process_index} ready.")        
        self.update_ap_status('running')
        while True:
            try:
                try:
                    msg: VDBDocTaskQueueMsg | VDBTaskExitMsg = self.task_queue.get(timeout=AP_SLEEP_TIME)
                except Empty:
                    self.update_ap_status('running')
                    continue
                if isinstance(msg, VDBTaskExitMsg):
                    log.debug('Process exit')
                    self.task_queue.put(msg)
                    self.update_ap_status('exit')
                    return
                log.info(f"Catched {msg.doc_task_id=}")
                log.debug(f"Catched {msg=}")            
                with SqlSyncSession() as session:
                    task = session.get(DocTasks, msg.doc_task_id)
                    if not task:
                        log.error(f"Task row not found")
                        continue
                    log.debug(f"{task.input_text=}")
                    try:
                        vdb_ops = VectorDBOps(msg.gvdbs_type, msg.gvdbs_url)
                        if error_msg := vdb_ops.check_url():
                            raise Exception(f'VDB URL error: {error_msg}')
                        start_time = time()
                        result_dict = vdb_ops.get_docs(
                            emb_obj=emb_models.get_by_name(msg.gvdbs_emb_model),
                            collection_name=msg.gvdbs_collection,
                            query_text=task.input_text
                        )
                        self.save_results_to_sql(
                            session=session,
                            task=task,
                            result_dict=result_dict,
                            vdb_query_seconds=round(time()-start_time, 3)
                        )
                    except Exception:
                        self.save_error_to_sql(
                            session=session, 
                            task=task, 
                            error_msg=f'Error during VectorDB search documents (doc_task_id={msg.doc_task_id})',
                            exc_msg=format_exc()
                        )
            except (KeyboardInterrupt, SystemExit):
                log.debug('Process exit')
                try:
                    self.update_ap_status('exit')
                except Exception:
                    pass
                return
            except Exception:
                log.error(f"Undefined exception:\n{format_exc()}")


class AllVDBWorkers:
    def __init__(self) -> None:
        self.num_to_start = self._get_num_to_start()
        self.processes: list[VDBWorker] = []
        self.task_queue = Queue()

    def _get_num_to_start(self) -> int:
        """
        Get number of VDB processes to start:
        Should be as specified in .env -> RT_VDB_PROCESS_NUM.
        Minimum 1, maximum as (cpu cores count - 1).
        """
        return max(min(cpu_count() - 1, int(RT_VDB_PROCESS_NUM)), 1)

    def start_all(self):
        log.info(f'Starting VDB Workers (Total: {self.num_to_start})')
        for p_index in range(1, self.num_to_start + 1):
            self.processes.append(VDBWorker(p_index, self.task_queue))
            self.processes[-1].start()
            log.info(f'VDB Worker {p_index} started')
        log.info('All VDB Workers started')

    def join_all(self):
        for process in self.processes:
            process.join()
