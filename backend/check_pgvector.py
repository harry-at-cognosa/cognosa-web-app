from time import time
from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.emb_models import EmbModels
from tasks_lib.vdb_lib.pgvector_ops import PGVectorOps

POSTGRESQL_URL = "postgresql://postgres:12345678@localhost:5432/cwa_db"
COLLECTION_NAME = 'collection_1'
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
QUERY_TEXT = "RAG development"

pgvector_ops = PGVectorOps(ParsedUrl.from_url(POSTGRESQL_URL))
emb_obj = EmbModels(preload_emb_models=True)

t1 = time()
results = pgvector_ops.get_docs(emb_obj.get_by_name(TRANSFORMER_MODEL), COLLECTION_NAME, QUERY_TEXT, gvdbs_cfg_json={'k': 10})
# print(f"Found {len(results)} documents")
for doc in results:
    print(f"Content: {doc['page_content'][:1000]}...")
    print(f"Source: {doc['metadata']}")
    print("---")

if not results:
    print(f"Nothing found!")
took_time = time() - t1
print(f"Query took time: {took_time:.3f}s")
