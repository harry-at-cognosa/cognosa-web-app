from threading import Thread
from traceback import format_exc
from sqlalchemy import select, func
from common import log
from common.enums.doc_task_status import TaskStatus
from common.sql_models import ApiSettings, DocTasks, GroupContexts
from common.sql_db_sync import SqlSyncSession, Session
from tasks_lib.entities.llm_worker_msg import LLMWorkerMsg
from tasks_lib.llm_lib.llm_ops import LLMOps


class LLMOptionsNotFound(Exception):
    pass

class LLMGroupContextNotFound(Exception):
    pass

class LLMGroupContextWrong(Exception):
    pass


class LLMWorker(Thread):
    def __init__(self, msg: LLMWorkerMsg) -> None:
        super().__init__()
        self.msg = msg
        self.doc_task_id = msg.doc_task_id

    def get_api_settings(self, session: Session) -> dict[str, str]:
        api_settings: dict[str, str] = {
            'llm_api_base': '',
            'llm_model_name': '',
            'llm_api_key': ''
        }
        for name, value in session.query(ApiSettings.name, ApiSettings.value):
            if name in api_settings:
                api_settings[name] = value.strip()
        
        if not all(api_settings.values()):
            log.error(f"Not all LLM options specified in api_settings:\n{api_settings}")
            raise LLMOptionsNotFound
        return api_settings
        
    def write_status_error(self, session: Session, task: DocTasks, error_msg: str, exc_msg: str | None = None):
        log.error(f"LLM run error in {task.doc_task_id=}:\n{error_msg=}{exc_msg=}")
        exc_msg = exc_msg if exc_msg else error_msg
        task.status_text = error_msg[:1000]
        task.exc_text = exc_msg[:20000]
        task.status = TaskStatus.QD_LLM_ERROR
        task.completed_at = func.now()        
        session.commit()

    def write_llm_writing(self, session: Session, task: DocTasks, answer: str):
        task.status = TaskStatus.QD_LLM_WRITING
        task.status_text = "LLM answering..."
        task.output_text = answer
        session.commit()
    
    def write_llm_finished(self, session: Session, task: DocTasks, answer: str):
        task.status = TaskStatus.QD_LLM_FETCHED
        task.status_text = "Task completed"
        task.output_text = answer
        task.completed_at = func.now()
        session.commit()

    def fetch_group_context(self, session: Session, task: DocTasks) -> GroupContexts:
        stmt = select(GroupContexts).where(
            GroupContexts.gc_id == task.gc_id,
            GroupContexts.group_id == task.group_id)
        result = session.execute(stmt).scalar_one_or_none()
        if not result:
            raise LLMGroupContextNotFound
        gc_text = result.gc_text.strip()
        if not gc_text:
            raise LLMGroupContextNotFound
        if not all(x in gc_text for x in ['{context}', '{question}']):
            raise LLMGroupContextWrong
        return result

    def run(self) -> None:
        log.info(f"Starting LLM task ID {self.doc_task_id}...")
        try:
            with SqlSyncSession() as session:
                task = session.get(DocTasks, self.doc_task_id)
                if not task:
                    raise Exception(f"LLM run error: tasks.task_id={self.doc_task_id} not found")
                try:
                    api_settings = self.get_api_settings(session)
                except LLMOptionsNotFound:
                    self.write_status_error(session, task, error_msg="LLM Options not found")
                    raise
                try:
                    group_context = self.fetch_group_context(session, task)                    
                except LLMGroupContextNotFound:
                    exc_msg = f"group_contexts row not found for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}"
                    self.write_status_error(session, task, error_msg="LLM Group Context not found", exc_msg=exc_msg)
                    raise
                except LLMGroupContextWrong:
                    exc_msg = f"group_contexts.gc_text is wrong for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}"
                    self.write_status_error(session, task, error_msg="LLM Group Context text is wrong", exc_msg=exc_msg)
                    raise
                try:
                    llm_ops = LLMOps(
                        query_text=task.input_text,
                        optional_text=task.optional_text,
                        template=group_context.gc_text,
                        context_json_str=task.context_json,
                        llm_api_base=api_settings['llm_api_base'],
                        llm_model_name=api_settings['llm_model_name'],
                        llm_api_key=api_settings['llm_api_key']
                    )
                    answer = ''
                    for chunk in llm_ops.stream_to_llm():
                        answer += chunk
                        self.write_llm_writing(session, task, answer)                    
                except Exception:
                    exc_msg = f"LLMOps exception for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}:\n{format_exc()}"
                    self.write_status_error(session, task, error_msg="Undefined LLM error", exc_msg=exc_msg)
                    raise
                else:
                    self.write_llm_finished(session, task, llm_ops.answer)
        
        except Exception:
            log.error(format_exc())
        log.info(f"Finished LLM task ID {self.doc_task_id}")
