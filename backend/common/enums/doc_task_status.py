class TaskStatus:
    QD_INIT = 0          # Query Document task: initial status (when user asks)
    QD_INIT_FETCHED = 1  # Query Document task: fetched by run_tasks
    QD_INIT_ERROR = -1   # Query Document task: error in task
    QD_VDB_PENDING = 2   # Query Document task: run_tasks start query to ChromaDB
    QD_VDB_FETCHED = 3   # Query Document task: run_tasks received documents from ChromaDB
    QD_VDB_ERROR = -3    # Query Document task: ChromaDB error
    QD_LLM_PENDING = 4   # Query Document task: run_tasks start query to LLM
    QD_LLM_WRITING = 5   # Query Document task: run_tasks received partial answer from LLM
    QD_LLM_FETCHED = 6   # Query Document task: run_tasks received answer from LLM
    QD_LLM_ERROR = -6    # Query Document task: LLM error
    QD_CANCELLED = -7    # Query Document task: cancelled by the user (any stage)
    QD_TIMEOUT = -8      # Query Document task: abandoned by the web app's stale-task sweep

    ERROR_LIST = [QD_INIT_ERROR, QD_VDB_ERROR, QD_LLM_ERROR, QD_CANCELLED, QD_TIMEOUT]
    FINISHED_LIST = ERROR_LIST + [QD_LLM_FETCHED, ]
    COMPLETED_SUCCESSFULLY = QD_LLM_FETCHED

    @classmethod
    def get_pct(cls, cur_status: int) -> int:
        """
        Get processing status in percents
        """
        if cur_status in cls.FINISHED_LIST:
            return 100
        if cls.COMPLETED_SUCCESSFULLY:
            return int(100.0 * cur_status / cls.COMPLETED_SUCCESSFULLY)
        return 0


# Stale-task sweep (applied by the web app when a task is read, see
# cwa_lib.sql_tables.doc_tasks.DocTasksTable.sweep_stale). A task that is still
# in flight is abandoned when either:
#   * no run_tasks watchdog heartbeat is live and the current stage is older
#     than TASK_ABANDON_NO_RUNNER_SEC (the runner died or was never started), or
#   * the current stage is older than TASK_TIMEOUT_SEC regardless of the runner
#     (a stalled vector search or LLM call).
# The current stage starts at coalesce(context_at, fetched_at, created_at).
TASK_ABANDON_NO_RUNNER_SEC = 60
TASK_TIMEOUT_SEC = 900
