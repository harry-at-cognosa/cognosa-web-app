###
# Document loader for PostgreSQL -> pgvector

POSTGRESQL_URL = "postgresql://postgres:12345678@localhost:5432/cwa_db"


# documents path from /backend folder.
DOCUMENTS_PATH = "../documents_for_chromadb"
COLLECTION_NAME = "collection_1"
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# Maximum number of single document processes. Each one takes ~700MB RAM
# It will be anyway less than CPU cores count - 1
MAX_PROCESSES = 16


import os
from dataclasses import dataclass
from multiprocessing import Process, Queue, cpu_count
from threading import Thread
from pathlib import Path
from time import time
from typing import Literal

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from common import WORK_DIR, log
from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.emb_models import HuggingFaceEmbeddings, EmbModels
from tasks_lib.vdb_lib.pgvector_ops import PGVectorOps
from tasks_lib.vdb_lib.vdb_ops import VectorDBOps

DOCUMENTS_PATH = os.path.normpath(os.path.join(WORK_DIR, DOCUMENTS_PATH))


log.init(prefix='document_loader_pgvector')

@dataclass
class DocFile:
    path: str
    type: Literal['pdf', 'docx', 'pptx', 'html', 'txt', 'csv', 'xlsx']

@dataclass
class MsgExit:
    exit: bool = True

@dataclass
class MsgFileFinished:
    path: str

class LogThread(Thread):
    def __init__(self, total_files: int, result_queue: Queue):
        super().__init__()
        self.total_files = total_files
        self.result_queue = result_queue
        self.processed = 0

    def run(self):
        while True:
            msg = self.result_queue.get()
            if isinstance(msg, MsgExit):
                return
            if isinstance(msg, MsgFileFinished):
                self.processed += 1
                print(f"Files processed {self.processed}/{self.total_files}")


class SingleDocumentProcess(Process):
    def __init__(self, process_index: int, msg_queue: Queue, result_queue: Queue):
        super().__init__()
        self.process_index = process_index
        self.msg_queue = msg_queue
        self.result_queue = result_queue

        self.collection_name = COLLECTION_NAME        

    def load_document(self, doc_file: DocFile) -> list[Document]:
        if doc_file.type == 'pdf':
            loader = PyPDFLoader(doc_file.path)
        elif doc_file.type == 'docx':
            loader = Docx2txtLoader(doc_file.path)
        elif doc_file.type == 'pptx':
            loader = UnstructuredPowerPointLoader(doc_file.path)
        elif doc_file.type == 'html':
            loader = UnstructuredHTMLLoader(doc_file.path)
        elif doc_file.type == 'txt':
            loader = TextLoader(doc_file.path, encoding='utf8', autodetect_encoding=True)
        elif doc_file.type == 'csv':
            loader = CSVLoader(doc_file.path, autodetect_encoding=True)
        elif doc_file.type == 'xlsx':
            loader = UnstructuredExcelLoader(doc_file.path)
        else:
            return []
        return loader.load()

    def process_file(self, doc_file: DocFile):
        doc_list = self.load_document(doc_file)
        if not doc_list:
            log.error(f"Failed to load file: {doc_file.path}")
            return
        split_docs = self.text_splitter.split_documents(doc_list)
        if not split_docs:
            log.error(f"Failed to get chunks from file: {doc_file.path}")
            return
        log.debug(f"Split into {len(split_docs)} chunks")
        self.pgvector_ops.save_to_pgvector(self.emb_obj.get_by_name(TRANSFORMER_MODEL), self.collection_name, split_docs)

    def run(self):
        log.init(prefix=f'document_loader_pgvector_{self.process_index}')
        self.pgvector_ops = PGVectorOps(ParsedUrl.from_url(POSTGRESQL_URL))
        self.emb_obj = EmbModels()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        while True:
            msg: DocFile | MsgExit = self.msg_queue.get()
            if isinstance(msg, MsgExit):
                self.msg_queue.put(msg)
                return
            if isinstance(msg, DocFile):
                try:
                    self.process_file(msg)
                except Exception as exc:
                    log.error(f"Exception for file {msg.path} : {exc}")
                self.result_queue.put(MsgFileFinished(msg.path))

class DocumentLoader:
    def __init__(self):
        self.documents_folder = Path(DOCUMENTS_PATH)
        self.collection_name = COLLECTION_NAME
        self.vdb_ops = VectorDBOps('pgvector', POSTGRESQL_URL)
        if error_msg := self.vdb_ops.check_url():
            print(f"Wrong {POSTGRESQL_URL=} : {error_msg}")
            exit(-1)
        self.pgvector_ops = PGVectorOps(self.vdb_ops.parsed_url)
        self.start_time = time()
        log.info(f"Initialized DocumentLoader with folder: {DOCUMENTS_PATH}")
        self.file_list: list[DocFile] = []
        self.process_list: list[SingleDocumentProcess] = []
        self.result_queue = Queue()

    def start(self):
        self.file_list = self.get_file_list()
        if not self.file_list:
            log.error("No files found to process")
            return
        log.info(f"Found {len(self.file_list)} files to process")
        self.log_thread = LogThread(len(self.file_list), self.result_queue)
        self.log_thread.start()
        self.create_collection()
        self.start_processes()
        self.result_queue.put(MsgExit())
        self.log_thread.join()
        used_time = time() - self.start_time
        log.info(f"Document processing completed successfully! Took {used_time:.2f} seconds")

    def create_collection(self):
        if self.pgvector_ops.collection_exists(self.collection_name):
            log.info(f"Collection {self.collection_name} is already exists")
            return
        log.info(f"Creating collection {self.collection_name}...")
        emb_obj = HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL)
        self.pgvector_ops.create_collection(emb_obj, self.collection_name)
        
    def start_processes(self):
        process_count = max(min(cpu_count() - 1, len(self.file_list)), 1)
        process_count = min(process_count, int(MAX_PROCESSES))
        log.info(f"Starting {process_count} loader processes...")
        msg_queue = Queue()
        for process_index in range(1, process_count + 1):
            self.process_list.append(SingleDocumentProcess(process_index, msg_queue, self.result_queue))
            self.process_list[-1].start()
        for doc_file in self.file_list:
            msg_queue.put(doc_file)
        
        msg_queue.put(MsgExit())
        for document_process in self.process_list:
            document_process.join()

    def get_file_list(self) -> list[DocFile]:
        file_list: list[DocFile] = []
        for root, _, files in self.documents_folder.walk():
            for f_name in files:
                f_path = os.path.normpath(os.path.join(root, f_name))
                f_ext = f_path.split('.')[-1].lower()
                if f_ext == 'pdf':
                    doc_file = DocFile(f_path, 'pdf')
                elif f_ext == 'docx':
                    doc_file = DocFile(f_path, 'docx')
                elif f_ext == 'pptx':
                    doc_file = DocFile(f_path, 'pptx')
                elif f_ext in ('htm', 'html'):
                    doc_file = DocFile(f_path, 'html')
                elif f_ext in ('txt', 'md'):
                    doc_file = DocFile(f_path, 'txt')
                elif f_ext == 'csv':
                    doc_file = DocFile(f_path, 'csv')
                elif f_ext == 'xlsx':
                    doc_file = DocFile(f_path, 'xlsx')
                else:
                    continue
                file_list.append(doc_file)
        return file_list
        

if __name__ == "__main__":
    DocumentLoader().start()
