class GroupVDBsTasksStatus:
    GVT_INIT = 0          # new task
    GVT_PENDING = 1       # still doing
    GVT_FINISHED = 9      # task completed

class GroupVDBsTasksTypes:
    REFRESH_METADATA_SELECT_VALUES = 1
