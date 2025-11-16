from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from common import log
from common.sql_db_sync import Engine, Session, get_sessionmaker
from common.sql_models import DocTasks
from common.enums.doc_task_status import TaskStatus
from tasks_lib.qd_lib.qd_init import QueryDocumentInit, QueryDocumentInitException
from tasks_lib.qd_lib.qd_vdb_fetched import QueryDocumentVectorDBFetched
from tasks_lib.vdb_lib.workers import AllVDBWorkers


class MainIteration:
    STATUS__NOT_FOUND = 0
    STATUS__PROCESSED_ONE = 1
    STATUS__UNDEFINED_ERROR = -1
    STATUS__TASK_ERROR = -2
    STATUS__SQL_ERROR = -3
    
    def __init__(self, engine: Engine, all_vdb_workers: AllVDBWorkers) -> None:
        self.engine = engine
        self.all_vdb_workers = all_vdb_workers
        self.vdb_task_queue = self.all_vdb_workers.task_queue
    
    def find_next_task(self, session: Session) -> DocTasks | None:
        """ 
        SELECT * FROM doc_tasks
        WHERE status IN (QD_INIT, QD_VDB_FETCHED) 
        ORDER BY doc_task_id 
        LIMIT 1
        FOR UPDATE SKIP LOCKED;
        """
        stmt = (
            select(DocTasks)
            .where(DocTasks.status.in_([TaskStatus.QD_INIT, TaskStatus.QD_VDB_FETCHED]))
            .order_by(DocTasks.doc_task_id.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def process_next_task(self) -> int:
        """Use get_session() to acquire session and process one task."""
        try:
            with get_sessionmaker(self.engine)() as session:
                task = self.find_next_task(session)
                if not task:
                    return self.STATUS__NOT_FOUND
                if (task.gvdbs_id) == -1 and (task.status == TaskStatus.QD_INIT):
                    # no document search, only ask LLM
                    task.status = TaskStatus.QD_VDB_FETCHED
                match task.status:
                    case TaskStatus.QD_INIT:  # Query Documents -> init
                        QueryDocumentInit(session, task, self.vdb_task_queue).run()

                    case TaskStatus.QD_VDB_FETCHED:  # Query Documents -> VectorDB data fetched
                        QueryDocumentVectorDBFetched(session, task).run()

                    case _:
                        log.error(f"Unexpected task status: {task.status}. Skipping.")
                        return self.STATUS__TASK_ERROR

                session.commit()
                log.info(f"Task {task.doc_task_id} updated to status {task.status}")
                return self.STATUS__PROCESSED_ONE
        except QueryDocumentInitException:
            return self.STATUS__TASK_ERROR
        except SQLAlchemyError as e:
            log.error(f"Database error: {e}")
            # Session is closed automatically
            return self.STATUS__SQL_ERROR
        except Exception as e:
            log.error(f"Unexpected error: {e}")
        return self.STATUS__UNDEFINED_ERROR
