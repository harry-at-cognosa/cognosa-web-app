from langchain_huggingface import HuggingFaceEmbeddings
from common import RT_VDB_EMB_MODELS_PRELOAD, log
from tasks_lib.cmd_line_opts import IS_DUMMY_VDB


class EmbModels:
    def __init__(self, preload_emb_models: bool = False) -> None:
        self.emb_model__obj: dict[str, HuggingFaceEmbeddings] = dict()
        if preload_emb_models:
            # preload embeddings specified in .env -> RT_VDB_EMB_MODELS_PRELOAD
            for emb_model in RT_VDB_EMB_MODELS_PRELOAD:
                self.load_embedding(emb_model)

    def load_embedding(self, emb_model: str):
        if IS_DUMMY_VDB:
            return
        if emb_model in self.emb_model__obj:
            return
        log.info(f"Loading embeddings model: {emb_model}...")
        self.emb_model__obj[emb_model] = HuggingFaceEmbeddings(
            model_name=emb_model,
            encode_kwargs={"normalize_embeddings": True},  # recommended for cosine similarity
        )
        log.info(f"Embeddings model: {emb_model} successfully loaded")

    def get_by_name(self, emb_model: str) -> HuggingFaceEmbeddings:
        if emb_model not in self.emb_model__obj:
            self.load_embedding(emb_model)
        return self.emb_model__obj[emb_model]
