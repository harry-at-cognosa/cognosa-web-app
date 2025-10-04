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

    ERROR_LIST = [QD_INIT_ERROR, QD_VDB_ERROR, QD_LLM_ERROR]
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
