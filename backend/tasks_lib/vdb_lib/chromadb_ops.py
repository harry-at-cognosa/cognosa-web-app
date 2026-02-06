from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from common import log
from common.parsed_url import ParsedUrl


class ChromaDBOps:
    def __init__(self, parsed_url: ParsedUrl):
        self.parsed_url = parsed_url
        self.host = self.parsed_url.host
        self.port = self.parsed_url.port

    def get_all_collection_names(self) -> list[str] | None:
        """
        Get all collection names on certain ChromaDB server
        """
        try:
            client = chromadb.HttpClient(host=self.host, port=self.port)
            return [collection.name for collection in client.list_collections()]
        except Exception as exc:
            log.error(f"Error while fetching collection names from ChromaDB host={self.host} port={self.port}: {exc}")
            return None
    
    def collection_exists(self, collection_name: str) -> bool | None:
        """Check if collection exists. None if server is not responding"""
        all_collection_names = self.get_all_collection_names()
        if all_collection_names is None:
            return None
        return collection_name in all_collection_names

    def get_docs(self, emb_obj: HuggingFaceEmbeddings, collection_name: str, query_text: str, retr_params: dict) -> list[dict]:
        client = chromadb.HttpClient(host=self.host, port=self.port)
        vectorstore = Chroma(
            client=client, 
            collection_name=collection_name, 
            embedding_function=emb_obj
        )
        # Create retriever
        retriever = vectorstore.as_retriever(**retr_params)        
        
        # Retrieve documents first
        docs = retriever.invoke(query_text)
        
        # return as list of dictionaries
        return [dict(d) for d in docs]
