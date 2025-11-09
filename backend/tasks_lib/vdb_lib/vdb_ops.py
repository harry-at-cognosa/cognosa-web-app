from time import sleep
from langchain_huggingface import HuggingFaceEmbeddings
from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.chromadb_ops import ChromaDBOps
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
from tasks_lib.vdb_lib.pgvector_ops import PGVectorOps
from tasks_lib.cmd_line_opts import IS_DUMMY_VDB


class VectorDBOps:
    def __init__(self, vdb_type: str, url: str) -> None:
        self.vdb_type = vdb_type
        self.url = url
        self.parsed_url = ParsedUrl.from_url(self.url)

    def check_url(self) -> str:
        """
        Check URL. Return error message if wrong.
        """
        if not self.parsed_url.host:
            return 'No host specified'
        if not self.parsed_url.port:
            return 'No port specified'
        if self.vdb_type == 'pgvector':
            if not self.parsed_url.user:
                return 'No user specified'
            if not self.parsed_url.password:
                return 'No password specified'
            if not self.parsed_url.path:
                return 'No db specified'
        return ''
    
    def collection_exists(self, collection_name: str) -> bool | None:
        """Check if collection exists. None if server not responds"""
        match self.vdb_type:
            case 'chroma':
                return ChromaDBOps(self.parsed_url).collection_exists(collection_name)
            case 'qdrant':
                return QdrantOps(self.parsed_url).collection_exists(collection_name)
            case 'pgvector':
                return PGVectorOps(self.parsed_url).collection_exists(collection_name)
        raise NotImplementedError
    
    def get_docs(self, emb_obj: HuggingFaceEmbeddings, collection_name: str, query_text: str, gvdbs_cfg_json: dict) -> list[dict]:
        if IS_DUMMY_VDB:
            sleep(2)
            return [{'page_content': 'Fake page content', 'metadata': 'Fake metadata'}]
        match self.vdb_type:
            case 'chroma':
                return ChromaDBOps(self.parsed_url).get_docs(emb_obj, collection_name, query_text, gvdbs_cfg_json)
            case 'qdrant':
                return QdrantOps(self.parsed_url).get_docs(emb_obj, collection_name, query_text, gvdbs_cfg_json)
            case 'pgvector':
                return PGVectorOps(self.parsed_url).get_docs(emb_obj, collection_name, query_text, gvdbs_cfg_json)
        raise NotImplementedError
