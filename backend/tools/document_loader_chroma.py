import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from common import WORK_DIR

DOCUMENTS_PATH = os.path.join(WORK_DIR, "../documents_for_chromadb")
CHROMADB_PATH = os.path.join(WORK_DIR, "../chroma_db1")
COLLECTION_NAME = "collection_1"
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200



def load_documents(folder_path: str):
    docs = []
    for root, _, files in os.walk(folder_path):
        for f_name in files:
            f_path = os.path.normpath(os.path.join(root, f_name))
            f_ext = f_path.split('.')[-1].lower()
            try:
                if f_ext == 'pdf':
                    loader = PyPDFLoader(f_path)
                elif f_ext == 'docx':
                    loader = Docx2txtLoader(f_path)
                elif f_ext == 'pptx':
                    loader = UnstructuredPowerPointLoader(f_path)
                elif f_ext in ('htm', 'html'):
                    loader = UnstructuredHTMLLoader(f_path)
                elif f_ext in ('txt', 'md'):
                    loader = TextLoader(f_path, encoding='utf8', autodetect_encoding=True)
                elif f_ext == 'csv':
                    loader = CSVLoader(f_path, autodetect_encoding=True)
                elif f_ext == 'xlsx':
                    loader = UnstructuredExcelLoader(f_path)
                else:
                    continue
                docs.extend(loader.load())
            except Exception as exc:
                print(f"Failed to load file: {f_path}. {exc}")
                continue
    return docs

def query_chroma(query: str, top_k: int = 3):
    print("Loading ChromaDB...")
    vectordb = Chroma(
        persist_directory=CHROMADB_PATH,
        collection_name=COLLECTION_NAME,
        embedding_function=HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL)
    )
    print(f"Searching for: {query}")
    results = vectordb.similarity_search(query, k=top_k)
    print(f"{results=}")

    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(doc.page_content[:500])
        print(f"[Source: {doc.metadata}]")

def load_all_documents():
    print("Loading documents...")
    documents = load_documents(DOCUMENTS_PATH)
    print(f"Loaded {len(documents)} documents.")
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")
    print("Storing in ChromaDB...")
    Chroma.from_documents(
        documents=splits,
        collection_name=COLLECTION_NAME,
        embedding=HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL),
        persist_directory=CHROMADB_PATH
        )
    print("Documents successfully stored in ChromaDB.")

def list_documents():
    """List all unique documents stored in ChromaDB (by source metadata)."""
    print("Loading ChromaDB...")
    vectordb = Chroma(
        persist_directory=CHROMADB_PATH,
        collection_name=COLLECTION_NAME,        
        embedding_function=HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL)
    )

    print("Fetching stored documents...")
    all_docs = vectordb.get()  # returns dict with ids, embeddings, documents, metadatas

    sources = {meta.get("source", "unknown") for meta in all_docs["metadatas"]}
    print("\nDocuments in ChromaDB:")
    for src in sources:
        print(" -", src)

if __name__ == "__main__":
    load_all_documents()
    # list_documents()
    # query_chroma(query="The Feedback Prize was a series of data analysis challenges hosted from 2020 to 2023")