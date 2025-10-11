from time import time
from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.emb_models import EmbModels
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps

QDRANT_URL = "127.0.0.1:6333"
COLLECTION_NAME = 'collection_1'
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
QUERY_TEXT = "RAG development"

qdrant_ops = QdrantOps(ParsedUrl.from_url(QDRANT_URL))
emb_obj = EmbModels(preload_emb_models=True)

t1 = time()
results = qdrant_ops.get_docs(emb_obj.get_by_name(TRANSFORMER_MODEL), COLLECTION_NAME, QUERY_TEXT)
# print(f"Found {len(results)} documents")
for doc in results:
    print(f"Content: {doc['page_content'][:1000]}...")
    print(f"Source: {doc['metadata']}")
    print("---")

if not results:
    print(f"Nothing found!")
took_time = time() - t1
print(f"Query took time: {took_time:.3f}s")
