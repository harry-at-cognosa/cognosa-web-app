from dataclasses import dataclass

@dataclass
class LLMWorkerMsg:
    doc_task_id: int
