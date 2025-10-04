from dataclasses import dataclass

@dataclass
class VDBDocTaskQueueMsg:
    doc_task_id: int
    group_id: int
    user_id: int
    gvdbs_type: str
    gvdbs_url: str    
    gvdbs_collection: str
    gvdbs_emb_model: str


@dataclass
class VDBTaskExitMsg:
    exit: bool = True
