###
# Check ChromaDB server is working
#
# Usage:
# python3 check_chroma_server.py
#
# or with parameters (group_id = 1, query = "Give me some documents"):
# python3 check_chroma_server.py -g 1 -q "Give me some documents"
#
###
import argparse
import json
from multiprocessing import Queue
from traceback import format_exc
from common import log
from common.parsed_url import ParsedUrl
from common.sql_db_sync import get_engine_sessionmaker
from common.sql_models import DocTasks, GroupVDBs
from tasks_lib.qd_lib.qd_init import QueryDocumentInit
from tasks_lib.vdb_lib.emb_models import EmbModels
from tasks_lib.vdb_lib.chromadb_ops import ChromaDBOps

log.init('check_chroma_server')

default_check_query = "What is the capital of Germany?"

class QDInitPatched(QueryDocumentInit):
    def write_status_init_error(self, error_msg: str):
        print(error_msg)

    def check_task_opts(self):
        # Checks:
        # input_text must be non-empty
        self.error_msg = ''
        try:
            self.error_msg = "No input text"
            self.input_text = self.input_text.strip()
            if not self.input_text:
                raise Exception
            self.error_msg = "No VectorDB settings found for this group"
            gvdbs_dict = json.loads(self.task.gvdbs_json)
            if not gvdbs_dict:
                raise Exception
            gvdbs = GroupVDBs(**gvdbs_dict)
            self.error_msg = 'VectorDB URL is not specified'
            self.gvdbs_url = gvdbs.gvdbs_url.strip()
            if not self.gvdbs_url:
                raise Exception
            self.gvdbs_parsed_url = ParsedUrl.from_url(self.gvdbs_url)
            if not self.gvdbs_parsed_url.host:
                raise Exception
            self.error_msg = 'VectorDB URL is wrong'
            if not self.gvdbs_parsed_url.port:
                raise Exception
            self.error_msg = 'VectorDB Collection is not specified'
            self.gvdbs_collection = gvdbs.gvdbs_collection.strip()
            if not self.gvdbs_collection:
                raise Exception
            self.error_msg = 'VectorDB Embeddings Model is not specified'
            self.gvdbs_emb_model = gvdbs.gvdbs_emb_model.strip()
            if not self.gvdbs_emb_model:
                raise Exception
        except Exception:
            pass
        else:
            self.error_msg = ''
            

def check_chroma(check_query: str, group_id: int):
    log.info("Checking ChromaDB server...")
    emb_models = EmbModels()
    engine, sessionmaker = get_engine_sessionmaker()
    with sessionmaker() as session:
        task = DocTasks()
        task.input_text = check_query
        task.group_id = group_id
        qd_init = QDInitPatched(session, task, Queue())
        log.info("Settings:")
        log.info(f"Group ID: {qd_init.task.group_id}")
        log.info(f"Query text: {qd_init.input_text}")
        qd_init.check_task_opts()
        if qd_init.error_msg:
            log.error(qd_init.error_msg)
            return
        log.info(f"ChromaDB host: {qd_init.gvdbs_host}")
        log.info(f"ChromaDB port: {qd_init.gvdbs_port}")
        log.info(f"ChromaDB collection: {qd_init.gvdbs_collection}")
        log.info(f"ChromaDB emb model: {qd_init.gvdbs_emb_model}")
        try:
            chroma_ops = ChromaDBOps(qd_init.gvdbs_parsed_url)
            docs = chroma_ops.get_docs(
                emb_obj=emb_models.get_by_name(qd_init.gvdbs_emb_model),
                collection_name=qd_init.gvdbs_collection,
                query_text=qd_init.input_text
            )
        except Exception as exc:
            log.error(str(exc))
            log.debug(format_exc())
        else:
            log.info(f"Retrieved {len(docs)} documents. Saved to debug logs")
            log.debug(f"Docs json:\n{docs}")
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check chroma server is running")

    parser.add_argument("-q", "--query", required=False, type=str, default=default_check_query, help="Query to check")
    parser.add_argument("-g", "--group_id", required=False, type=int, default=1, help="Group ID")
    
    args = parser.parse_args()
    try:
        check_chroma(check_query=args.query, group_id=args.group_id)
    except Exception as exc:
        log.error(str(exc))
        log.debug(format_exc())