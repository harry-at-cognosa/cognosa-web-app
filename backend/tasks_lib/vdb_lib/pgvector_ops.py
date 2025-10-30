import warnings
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from common import log
from common.parsed_url import ParsedUrl
warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

class PGVectorOps:
    def __init__(self, parsed_url: ParsedUrl):
        self.parsed_url = parsed_url
        self.parsed_url.scheme = 'postgresql'
        self.connection_string = self.parsed_url.full_url

    def collection_exists(
            self,
            collection_name: str
        ) -> bool:
        """
        Check if a table (used as a vector collection) exists in the PostgreSQL database.
        """
        try:
            # URL-encode password in case it contains special characters
            engine = create_engine(self.parsed_url.full_url, echo=False)            
            with sessionmaker(bind=engine, expire_on_commit=False)() as session:
                result = session.execute(
                    text("SELECT name FROM langchain_pg_collection WHERE name = :name"),
                    {"name": collection_name}
                ).fetchone()
                return bool(result)
        except SQLAlchemyError as e:
            return False
        
    def get_vector_store(self, emb_obj: HuggingFaceEmbeddings, collection_name: str) -> PGVector:
        return PGVector(
            embedding_function=emb_obj,
            collection_name=collection_name,
            connection_string=self.connection_string,
            use_jsonb=True,
        )
    
    def create_collection(self, emb_obj: HuggingFaceEmbeddings, collection_name: str):
        """Create an empty vector store in PostgreSQL"""
        try:
            # Create empty PGVector store
            self.get_vector_store(emb_obj, collection_name)
            log.info(f"Created collection '{collection_name}'")
        except Exception as e:
            log.error(f"Error creating empty vector store: {str(e)}")
            raise
    
    def save_to_pgvector(
            self, 
            emb_obj: HuggingFaceEmbeddings, 
            collection_name: str, 
            documents: list, 
        ) -> str:
        """
        Save documents in PGVector vector database.
        
        Returns:
            Error message if exists
        """
        if not documents:
            log.error(error_msg := "No documents to store in PGVector")
            return error_msg
        try:
            vector_store = self.get_vector_store(emb_obj, collection_name)
            vector_store.add_documents(documents)
            log.info(f"Added {len(documents)} documents to PGVector collection '{collection_name}'")
            return ''
        except Exception as exc:
            log.error(f"Error storing documents in PGVector: {str(exc)}")
            return "Error storing documents in PGVector"

    def get_docs(self, emb_obj: HuggingFaceEmbeddings, collection_name: str, query_text: str) -> list[dict]:
        vectorstore = self.get_vector_store(emb_obj, collection_name)
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})                
        # Retrieve documents first
        docs = retriever.invoke(query_text)        
        # return as list of dictionaries
        return [dict(d) for d in docs]
