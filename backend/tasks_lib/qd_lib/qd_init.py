from datetime import datetime
import json
from multiprocessing import Queue
from common.sql_models import DocTasks, GroupVDBs
from common.sql_db_sync import Session
from common.enums.doc_task_status import TaskStatus
from tasks_lib.entities.task_queue_msg import VDBDocTaskQueueMsg

class QueryDocumentInitException(Exception):
    pass

class QueryDocumentInit:
    def __init__(self, session: Session, task: DocTasks, vdb_task_queue: Queue) -> None:
        self.session = session
        self.task = task
        self.vdb_task_queue = vdb_task_queue
        self.input_text = self.task.input_text
        self.gvdbs_type = ''
        self.gvdbs_url = ''
        self.gvdbs_host = ''
        self.gvdbs_port = 8000
        self.gvdbs_collection = ''
        self.gvdbs_model = ''

    def write_status_init_error(self, error_msg: str):
        self.task.status = TaskStatus.QD_INIT_ERROR
        self.task.status_text = "Task init error"
        self.task.exc_text = error_msg
        self.session.commit()

    def write_status_init_fetched(self):
        self.task.status = TaskStatus.QD_INIT_FETCHED
        self.task.status_text = "Task fetched. Processing..."
        self.task.fetched_at = datetime.now()
        self.session.commit()
    
    def check_task_opts(self):
        # Checks:
        # input_text must be non-empty
        error_msg = ''
        try:
            error_msg = "No input text"
            self.input_text = self.input_text.strip()
            if not self.input_text:
                raise Exception
            error_msg = "No VectorDB settings found for this group and gvdbs_id"
            gvdbs_dict = json.loads(self.task.gvdbs_json)
            if not gvdbs_dict:
                raise Exception
            gvdbs = GroupVDBs(**gvdbs_dict)            
            self.gvdbs_type = gvdbs.gvdbs_type
            error_msg = 'VectorDB URL is not specified'
            self.gvdbs_url = gvdbs.gvdbs_url.strip()
            if not self.gvdbs_url:
                raise Exception
            error_msg = 'VectorDB Collection is not specified'
            self.gvdbs_collection = gvdbs.gvdbs_collection.strip()
            if not self.gvdbs_collection:
                raise Exception
            error_msg = 'VectorDB Embeddings Model is not specified'
            self.gvdbs_emb_model = gvdbs.gvdbs_emb_model.strip()
            if not self.gvdbs_emb_model:
                raise Exception
        except Exception:
            self.write_status_init_error(error_msg)
            raise QueryDocumentInitException
        
    def send_task_to_vdb_worker(self):
        # TODO: check queue filled
        self.vdb_task_queue.put(
            VDBDocTaskQueueMsg(
                doc_task_id=self.task.doc_task_id,
                user_id=self.task.user_id,
                group_id=self.task.group_id,
                gvdbs_type=self.gvdbs_type,
                gvdbs_url=self.gvdbs_url,
                gvdbs_collection=self.gvdbs_collection,
                gvdbs_emb_model=self.gvdbs_emb_model
                )
            )
        
    def run(self):
        self.check_task_opts()
        self.write_status_init_fetched()
        self.send_task_to_vdb_worker()
