from datetime import datetime
from common.sql_models import DocTasks
from common.sql_db_sync import Session
from common.enums.doc_task_status import TaskStatus
from tasks_lib.llm_lib.workers import LLMWorker, LLMWorkerMsg


class QueryDocumentVectorDBFetchedException(Exception):
    pass


class QueryDocumentVectorDBFetched:
    def __init__(self, session: Session, task: DocTasks) -> None:
        self.session = session
        self.task = task

    def write_status_llm_pending(self):
        self.task.status = TaskStatus.QD_LLM_PENDING
        self.task.context_at = datetime.now()
        self.session.commit()

    def send_task_to_llm_worker(self):
        llm_worker = LLMWorker(msg=LLMWorkerMsg(doc_task_id=self.task.doc_task_id))
        llm_worker.run()

    def run(self):
        self.write_status_llm_pending()
        self.send_task_to_llm_worker()
