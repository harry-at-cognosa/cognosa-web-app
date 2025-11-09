from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from common import log
from common.parsed_url import ParsedUrl


class QdrantOps:
    def __init__(self, parsed_url: ParsedUrl):
        self.parsed_url = parsed_url
        self.host = self.parsed_url.host
        self.port = self.parsed_url.port
        self.api_key: str | None = None
        if (self.parsed_url.user == 'api_key') and self.parsed_url.password:
            self.api_key = self.parsed_url.password
        self.client = QdrantClient(host=self.host, port=self.port, api_key=self.api_key)

    def collection_exists(self, collection_name: str) -> bool | None:
        """Check if collection exists. None if server not responds"""
        try:
            return self.client.collection_exists(collection_name)
        except Exception as exc:
            log.error(f"Error while fetching collection names from Qdrant host={self.host} port={self.port}: {exc}")
            return None
    
    def create_collection(self, emb_obj: HuggingFaceEmbeddings, collection_name: str):
        # Get embedding dimension by testing the model
        test_embedding = emb_obj.embed_query("test")
        vector_size = len(test_embedding)
    
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        log.info(f"Created collection '{collection_name}' with vector size {vector_size}")

    def save_to_qdrant(
            self, 
            emb_obj: HuggingFaceEmbeddings, 
            collection_name: str, 
            documents: list, 
            create_collection: bool = False
        ) -> str:
        """
        Save documents in Qdrant vector database.
        
        Returns:
            Error message if exists
        """
        if not documents:
            log.error(error_msg := "No documents to store in Qdrant")
            return error_msg
        try:
            if create_collection:
                self.create_collection(emb_obj, collection_name)
            # Create QdrantVectorStore and add documents
            vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=collection_name,
                embedding=emb_obj,
            )
            # Add documents to the vector store
            vector_store.add_documents(documents)
            log.info(f"Added {len(documents)} documents to Qdrant collection '{collection_name}'")
            return ''
        except Exception as e:
            log.error(f"Error storing documents in Qdrant: {str(e)}")
            return "Error storing documents in Qdrant"

    def get_docs(self, emb_obj: HuggingFaceEmbeddings, collection_name: str, query_text: str, gvdbs_cfg_json: dict) -> list[dict]:
        vectorstore = QdrantVectorStore(
                client=self.client,
                collection_name=collection_name,
                embedding=emb_obj,
            )
        # Create retriever
        retriever = vectorstore.as_retriever(**gvdbs_cfg_json)
        
        # Retrieve documents first
        docs = retriever.invoke(query_text)
        
        # return as list of dictionaries
        return [dict(d) for d in docs]
