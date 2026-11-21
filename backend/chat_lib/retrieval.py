"""Embedding and vector search for a chat turn.

Search goes through the same `QdrantOps.get_docs` the Queries runner uses, so
chat retrieves exactly as Queries does, filters included. Only Qdrant is
supported. Both the embedding and the search are blocking calls and run in
worker threads.
"""
import asyncio
import json
import os
from langchain_huggingface import HuggingFaceEmbeddings
from common import log
from common.features.gvdbs_retr_filters import GVDBsRetrFiltersFunctions
from common.helpers import split2list
from common.parsed_url import ParsedUrl
from common.sql_models import GroupVDBs
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps

# Optional comma-separated list of embedding models to load at start-up, so the
# first question after a restart does not wait for the model to load.
CHAT_EMB_MODELS_PRELOAD = split2list(os.getenv("CHAT_EMB_MODELS_PRELOAD", ''), ',', str)


class EmbeddingModels:
    """Embedding models, loaded on first use and kept for the life of the process."""
    def __init__(self) -> None:
        self._models: dict[str, HuggingFaceEmbeddings] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def _load(name: str) -> HuggingFaceEmbeddings:
        log.info(f"Chat: loading embedding model {name}...")
        model = HuggingFaceEmbeddings(
            model_name=name,
            encode_kwargs={"normalize_embeddings": True},  # as run_tasks does; needed for cosine similarity
        )
        log.info(f"Chat: embedding model {name} loaded")
        return model

    async def get(self, name: str) -> HuggingFaceEmbeddings:
        if name in self._models:
            return self._models[name]
        lock = self._locks.setdefault(name, asyncio.Lock())
        async with lock:  # two first questions at once load the model once
            if name not in self._models:
                self._models[name] = await asyncio.to_thread(self._load, name)
        return self._models[name]

    async def preload(self) -> None:
        for name in CHAT_EMB_MODELS_PRELOAD:
            try:
                await self.get(name)
            except Exception as exc:
                log.error(f"Chat: cannot preload embedding model {name}: {exc}")


embedding_models = EmbeddingModels()


def _search(emb_obj, gvdbs_url: str, collection: str, query: str, retr_params: dict, retr_filters) -> list[dict]:
    return QdrantOps(ParsedUrl.from_url(gvdbs_url)).get_docs(
        emb_obj=emb_obj,
        collection_name=collection,
        query_text=query,
        retr_params=retr_params,
        retr_filters=retr_filters,
    )


async def retrieve(collection: GroupVDBs, query: str, retr_params: dict, filters_json: str | None) -> list[dict]:
    """Chunks for `query` from the conversation's collection, as dicts with
    `page_content` and `metadata`. Used for one LLM call and then dropped."""
    emb_obj = await embedding_models.get(collection.gvdbs_emb_model)
    retr_filters = None
    if filters_json:
        retr_filters = GVDBsRetrFiltersFunctions.get_for_run_tasks(
            json.dumps({'filters': json.loads(filters_json)}), collection.gvdbs_retr_filters)
    # get_docs writes the filter into search_kwargs: give it its own copy
    params = {'search_type': retr_params['search_type'], 'search_kwargs': dict(retr_params['search_kwargs'])}
    docs = await asyncio.to_thread(
        _search, emb_obj, collection.gvdbs_url, collection.gvdbs_collection, query, params, retr_filters)
    return [d for d in docs if str(d.get('page_content', '')).strip()]
