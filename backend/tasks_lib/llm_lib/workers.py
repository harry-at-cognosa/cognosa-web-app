import json
from threading import Thread
from time import time
from traceback import format_exc
from sqlalchemy import select, update, func
from common import log
from common.enums.doc_task_status import TaskStatus
from common.sql_models import DocTasks, GroupContexts, GroupLLMs
from common.sql_db_sync import Session, get_engine_sessionmaker
from tasks_lib.entities.llm_worker_msg import LLMWorkerMsg
from tasks_lib.llm_lib.llm_ops import LLMOps
from tasks_lib.llm_lib.llm_errors import classify_llm_exception
from .tiktoken_count import TikTokenCount


class LLMOptionsNotFound(Exception):
    pass

class LLMGroupContextNotFound(Exception):
    pass

class LLMGroupContextWrong(Exception):
    pass

class LLMTaskCancelled(Exception):
    """The task left the in-flight statuses (cancelled by the user or swept as
    stale) while the LLM was still streaming. Nothing more may be written."""
    pass


def _db_text(s) -> str:
    """Strip NUL bytes: PostgreSQL rejects them in text columns, and PDF extraction
    can emit them. A NUL in sent_to_llm killed task 172 on 2026-10-11."""
    return str(s).replace('\x00', '') if s is not None else ''


class LLMWorker(Thread):
    def __init__(self, msg: LLMWorkerMsg) -> None:
        super().__init__()
        self.msg = msg
        self.doc_task_id = msg.doc_task_id
        self.tiktoken_count = TikTokenCount('')
        self._sent_written = False

    def get_llm_settings(self, task: DocTasks) -> GroupLLMs:
        try:
            gllms_dict = json.loads(task.gllms_json)
            return GroupLLMs(**gllms_dict)
        except Exception:
            log.error(f"LLM options not found for gllms_id={task.gllms_id}")
            raise LLMOptionsNotFound        
        
    def write_status_error(self, session: Session, task: DocTasks, error_msg: str, exc_msg: str | None = None):
        log.error(f"LLM run error in {task.doc_task_id=}:\n{error_msg=}{exc_msg=}")
        exc_msg = exc_msg if exc_msg else error_msg
        # A failed flush leaves the session unusable until rolled back; without
        # this the error itself cannot be written and the task stays "in progress".
        session.rollback()
        # Guarded like the streaming writes: a task the user cancelled (or the
        # sweep abandoned) keeps that status even if the stream then errors.
        stmt = (
            update(DocTasks)
            .where(
                DocTasks.doc_task_id == task.doc_task_id,
                DocTasks.status.notin_(TaskStatus.FINISHED_LIST),
            )
            .values(
                status_text=_db_text(error_msg)[:1000],
                exc_text=_db_text(exc_msg)[:20000],
                status=TaskStatus.QD_LLM_ERROR,
                completed_at=func.now(),
            )
        )
        if not session.execute(stmt).rowcount:
            log.info(f"LLM task {task.doc_task_id} already finished/cancelled; error not written")
        session.commit()

    @staticmethod
    def _update_if_live(session: Session, task: DocTasks, **values) -> None:
        """UPDATE the row only while it is still in flight.

        The cancel endpoint and the stale-task sweep move a task to a terminal
        status from outside this process. An unconditional ORM commit here would
        overwrite that, so every write during streaming is guarded on the status
        column and a zero rowcount raises LLMTaskCancelled to stop the stream.
        """
        stmt = (
            update(DocTasks)
            .where(
                DocTasks.doc_task_id == task.doc_task_id,
                DocTasks.status.notin_(TaskStatus.FINISHED_LIST),
            )
            .values(**values)
        )
        rowcount = session.execute(stmt).rowcount
        session.commit()
        if not rowcount:
            raise LLMTaskCancelled
        # Deliberately no setattr on `task`: a dirty ORM attribute would be
        # autoflushed as an unguarded UPDATE on the next execute.

    def write_sent_to_llm(self, session: Session, task: DocTasks, sent_to_llm: str):
        if sent_to_llm and not self._sent_written:
            self._update_if_live(
                session, task,
                sent_to_llm=_db_text(sent_to_llm),
                llm_tokens_sent=int(self.tiktoken_count.count(sent_to_llm)),
            )
            self._sent_written = True

    def _answer_column(self, task: DocTasks) -> str:
        return 'output_text' if task.question_number == 1 else 'output_text_2'

    def write_llm_writing(self, session: Session, task: DocTasks, answer: str):
        answer = _db_text(answer)
        self._update_if_live(
            session, task,
            status=TaskStatus.QD_LLM_WRITING,
            status_text="LLM answering...",
            llm_tokens_received=self.tiktoken_count.count(answer),
            **{self._answer_column(task): answer},
        )
    
    def write_llm_finished(self, session: Session, task: DocTasks, answer: str, llm_query_seconds: float):
        answer = _db_text(answer)
        self._update_if_live(
            session, task,
            status=TaskStatus.QD_LLM_FETCHED,
            status_text="Task completed",
            completed_at=func.now(),
            llm_query_seconds=llm_query_seconds,
            llm_tokens_received=self.tiktoken_count.count(answer),
            **{self._answer_column(task): answer},
        )

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
        engine, sessionmaker = get_engine_sessionmaker()
        try:
            with sessionmaker() as session:
                task = session.get(DocTasks, self.doc_task_id)
                if not task:
                    raise Exception(f"LLM run error: tasks.task_id={self.doc_task_id} not found")
                try:
                    gllms = self.get_llm_settings(task)
                except LLMOptionsNotFound:
                    self.write_status_error(session, task, error_msg="LLM Options not found")
                    raise
                gc_text = '{question}{context}'
                if task.gvdbs_id != -1:
                    try:
                        group_context = self.fetch_group_context(session, task)
                        gc_text = group_context.gc_text
                    except LLMGroupContextNotFound:
                        exc_msg = f"group_contexts row not found for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}"
                        self.write_status_error(session, task, error_msg="LLM Group Context not found", exc_msg=exc_msg)
                        raise
                    except LLMGroupContextWrong:
                        exc_msg = f"group_contexts.gc_text is wrong for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}"
                        self.write_status_error(session, task, error_msg="LLM Group Context text is wrong", exc_msg=exc_msg)
                        raise
                try:
                    self.tiktoken_count = TikTokenCount(gllms.gllms_model)
                    start_time = time()
                    llm_ops = LLMOps(
                        query_text=task.input_text,
                        optional_text=task.optional_text,
                        template=gc_text,
                        context_json_str=task.context_json,
                        llm_type=gllms.gllms_type,
                        llm_api_base=gllms.gllms_api_base,
                        llm_model=gllms.gllms_model,
                        llm_api_key=gllms.gllms_api_key,
                    )
                    answer = ''
                    for chunk in llm_ops.stream_to_llm():
                        answer += chunk
                        self.write_sent_to_llm(session, task, llm_ops.llm_obj.sent_to_llm)
                        self.write_llm_writing(session, task, answer)                                        
                except LLMTaskCancelled:
                    # Terminal status already written by whoever cancelled or
                    # swept the task; just stop streaming and leave it as is.
                    log.info(f"LLM task {task.doc_task_id} cancelled while streaming; stopping")
                    raise
                except Exception as exc:
                    exc_msg = f"LLMOps exception for {task.doc_task_id=}, {task.group_id=}, {task.gc_id=}:\n{format_exc()}"
                    self.write_status_error(session, task, error_msg=classify_llm_exception(exc), exc_msg=exc_msg)
                    raise
                else:
                    self.write_llm_finished(session, task, llm_ops.llm_obj.answer, llm_query_seconds=round(time()-start_time, 3))
        
        except LLMTaskCancelled:
            pass  # already logged where it was detected
        except Exception:
            log.error(format_exc())
        log.info(f"Finished LLM task ID {self.doc_task_id}")
        engine.dispose()
