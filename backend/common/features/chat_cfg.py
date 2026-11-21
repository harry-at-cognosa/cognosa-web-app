"""Chat (conversation mode) settings held per collection in `group_vdbs.gvdbs_chat_cfg`.

JSON, every key optional:

    {"search_type": "similarity", "search_kwargs": {"k": 8}, "system_prompt": "..."}

An empty value means: the collection's own default search type, with `k`
capped at CHAT_DEFAULT_K, and the built-in system prompt. Chat therefore works
on any collection without configuration.
"""
import json
from pydantic import BaseModel, field_validator
from .gvdbs_retr_params import (
    GVDBsRetrParams, GVDBsDefRetrParams, ALLOWED_SEARCH_TYPES, DEFAULT_RETR_PARAMS, DEFAULT_SEARCH_TYPE,
)

# Chat answers rarely need the 20-30 chunks the Queries workbench defaults to.
CHAT_DEFAULT_K = 8
# `chat_history_turns` setting: default and sanity bound.
CHAT_HISTORY_TURNS_DEFAULT = 6
CHAT_HISTORY_TURNS_MAX = 50

CHAT_DEFAULT_SYSTEM_PROMPT = (
    "You are an assistant answering questions about a document collection.\n"
    "Answer using the context below. If the context does not contain the answer, "
    "say that you do not know; do not make up an answer.\n"
    "When the context shows where a statement comes from, name that source.\n"
    "Keep answers concise unless asked for detail.\n"
    "\n"
    "Context:\n"
    "{context}"
)


class ChatCfg(BaseModel):
    search_type: str | None = None
    search_kwargs: dict | None = None
    system_prompt: str | None = None

    @field_validator("search_type")
    @classmethod
    def validate__search_type(cls, v):
        if v is not None and v not in ALLOWED_SEARCH_TYPES:
            raise ValueError(f"search_type must be one of {ALLOWED_SEARCH_TYPES}")
        return v

    @field_validator("system_prompt")
    @classmethod
    def validate__system_prompt(cls, v):
        if v is None or not v.strip():
            return None
        if '{context}' not in v:
            raise ValueError("system_prompt must contain {context}")
        return v

    @classmethod
    def from_str(cls, gvdbs_chat_cfg: str | None) -> 'ChatCfg':
        """Parse a stored value. A broken stored value falls back to defaults
        rather than taking chat down for that collection."""
        try:
            return cls.model_validate(json.loads(gvdbs_chat_cfg or '{}'))
        except Exception:
            return cls()

    @classmethod
    def validate_str(cls, gvdbs_chat_cfg: str) -> str:
        """Validate a value entered by a superuser; raises ValueError. Returns
        the normalised JSON to store."""
        try:
            raw = json.loads(gvdbs_chat_cfg or '{}')
        except Exception:
            raise ValueError("Chat settings must be valid JSON") from None
        if not isinstance(raw, dict):
            raise ValueError("Chat settings must be a JSON object")
        cfg = cls.model_validate(raw)
        if cfg.search_type or cfg.search_kwargs:
            # reject kwargs GVDBsRetrParams would silently replace by defaults
            sk = cfg.search_kwargs or {}
            for name in sk:
                if name not in ('k', 'fetch_k', 'lambda_mult', 'score_threshold'):
                    raise ValueError(f"Unknown search_kwargs key: {name}")
            for name in ('k', 'fetch_k'):
                if name in sk and not (isinstance(sk[name], int) and sk[name] > 0):
                    raise ValueError(f"search_kwargs.{name} must be a positive integer")
        return json.dumps(cfg.model_dump(exclude_none=True), indent=1)

    def get_system_prompt(self) -> str:
        return self.system_prompt or CHAT_DEFAULT_SYSTEM_PROMPT

    def get_retr_params(self, gvdbs_retr_params: str | dict) -> dict:
        """Retrieval parameters for a chat turn, as `{'search_type', 'search_kwargs'}`.

        Start from the collection's own defaults, capping k at CHAT_DEFAULT_K
        (and fetch_k in proportion for MMR); then apply whatever this chat
        configuration sets explicitly.
        """
        try:
            base = GVDBsDefRetrParams.from_dict(gvdbs_retr_params).as_dict()
        except Exception:
            base = DEFAULT_RETR_PARAMS
        search_type = self.search_type or base.get('search_type') or DEFAULT_SEARCH_TYPE
        kwargs = dict(base.get('search_kwargs__' + search_type) or {})
        base_k = int(kwargs.get('k', CHAT_DEFAULT_K))
        if base_k > CHAT_DEFAULT_K:
            if 'fetch_k' in kwargs:
                # keep the collection's fetch_k/k ratio
                kwargs['fetch_k'] = max(CHAT_DEFAULT_K, round(int(kwargs['fetch_k']) * CHAT_DEFAULT_K / base_k))
            kwargs['k'] = CHAT_DEFAULT_K
        kwargs.update(self.search_kwargs or {})
        if 'fetch_k' in kwargs and int(kwargs['fetch_k']) < int(kwargs['k']):
            kwargs['fetch_k'] = int(kwargs['k'])  # MMR cannot return more than it fetches
        return GVDBsRetrParams.from_str(json.dumps({'search_type': search_type, 'search_kwargs': kwargs})).as_dict()


def parse_chat_history_turns(value: str | None) -> int:
    """`api_settings.chat_history_turns` as an int; missing or invalid -> default."""
    try:
        n = int(str(value).strip())
        if 1 <= n <= CHAT_HISTORY_TURNS_MAX:
            return n
    except Exception:
        pass
    return CHAT_HISTORY_TURNS_DEFAULT
