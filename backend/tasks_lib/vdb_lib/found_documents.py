import json
from common.sql_models import DocTasks

class FoundDocuments:
    """
    Make `doc_tasks`.`context_json` from found documents.
    For follow-up questions (doc_tasks.question_number > 1): 
        add only new documents (with new page_content)
    """
    def __init__(self, task: DocTasks):
        self.task = task
        self.old_list = self._get_old_list()
        self.old_page_contents = {str(d['page_content']) for d in self.old_list}
    
    def _get_old_list(self) -> list[dict]:
        if self.task.question_number <= 1:
            return []
        try:
            old_list = json.loads(self.task.context_json or '[]')
            return [d for d in old_list if d.get('page_content', '').strip()]
        except Exception:
            return []

    def append(self, result_list: list[dict]):
        try:
            new_list = self.old_list
            item_seqn = len(self.old_list)
            for doc_dict in result_list:
                page_content = doc_dict.get('page_content', '').strip()
                if not page_content:
                    continue
                if page_content in self.old_page_contents:
                    continue
                item_seqn += 1
                doc_dict['item_seqn'] = item_seqn
                doc_dict['question_seqn'] = self.task.question_number                
                new_list.append(doc_dict)
            context_json=json.dumps(new_list, indent=1)
            self.task.context_json = context_json
        except Exception:
            context_json = json.dumps([{'error': 'Undefined error in found documents'}], indent=1)