from time import time, sleep
from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.emb_models import EmbModels
from tasks_lib.vdb_lib.pgvector_ops import PGVectorOps

POSTGRESQL_URL = "postgresql://postgres:12345678@localhost:5432/cwa_db"
COLLECTION_NAME = 'collection_1'
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
QUERY_TEXT = "RAG development"

pgvector_ops = PGVectorOps(ParsedUrl.from_url(POSTGRESQL_URL))
emb_obj = EmbModels(preload_emb_models=True)

while True:
    t1 = time()
    results = pgvector_ops.get_docs(emb_obj.get_by_name(TRANSFORMER_MODEL), COLLECTION_NAME, QUERY_TEXT)
    # print(f"Found {len(results)} documents")
    for doc in results:
        print(f"Content: {doc['page_content'][:1000]}...")
        print(f"Source: {doc['metadata']}")
        print("---")

    print(time() - t1)
    exit(-1)
    sleep(1)