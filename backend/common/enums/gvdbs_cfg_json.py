import json
from typing import Literal

SEARCH_TYPES = Literal['similarity', 'mmr', 'similarity_score_threshold']

DEFAULT_SEARCH_TYPE = 'similarity'
DEFAULT_dicts = {
    'similarity': {
        'search_type': 'similarity', 
        'search_kwargs': {'k': 10}
    },
    'mmr': {
        'search_type': 'mmr', 
        'search_kwargs': {'k': 10, 'fetch_k': 20, 'lambda_mult': 0.5}
    },
    'similarity_score_threshold': {
        'search_type': 'similarity_score_threshold', 
        'search_kwargs': {'k': 10, 'score_threshold': 0.5}
    }
}

class GVDBsCfgJSON:
    """
    'search_type' (Optional[str]) 
    Defines the type of search that the Retriever should perform.
    Can be 'similarity' (default), 'mmr', or 'similarity_score_threshold'.
    'search_kwargs' (Optional[Dict])
    Keyword arguments to pass to the search function. Can include things like:
        k: Amount of documents to return (Default: 4) 
        score_threshold: Minimum relevance threshold for similarity_score_threshold
        fetch_k: Amount of documents to pass to MMR algorithm (Default: 20) 
        lambda_mult: Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum. (Default: 0.5)
    """
    ALLOWED_SEARCH_TYPES = ['similarity', 'mmr', 'similarity_score_threshold']
    
    def __init__(self, search_type: SEARCH_TYPES, search_kwargs: dict[str, int | float]):
        self.search_type: SEARCH_TYPES = search_type
        self.search_kwargs = search_kwargs
    
    def as_dict(self) -> dict:
        return {
            'search_type': self.search_type,
            'search_kwargs': self.search_kwargs
        }
    
    def to_short_str(self) -> str:
        k = str(self.search_kwargs.get('k'))
        fetch_k = str(self.search_kwargs.get('fetch_k'))
        lambda_mult = str(self.search_kwargs.get('lambda_mult'))
        score_threshold = str(self.search_kwargs.get('score_threshold'))
        if self.search_type == 'similarity':
            return "SIM: " + k
        if self.search_type == 'mmr':
            return "MMR: " + k + "/" + fetch_k + "/" + lambda_mult
        return "SST: " + k + "/" + score_threshold

    @staticmethod
    def from_dict(gvdbs_cfg_json: str | dict):
        try:
            cfg_dict = gvdbs_cfg_json if isinstance(gvdbs_cfg_json, dict) else json.loads(gvdbs_cfg_json)
            # search_type
            search_type: SEARCH_TYPES = cfg_dict.get('search_type', DEFAULT_SEARCH_TYPE)
            if search_type not in GVDBsCfgJSON.ALLOWED_SEARCH_TYPES:
                raise Exception
            # search_kwargs
            sk: dict = dict(cfg_dict.get('search_kwargs', dict()))
            def_sk_dict = DEFAULT_dicts.get(search_type, dict())
            search_kwargs: dict[str, int | float] = {
                'k': int(sk.get('k', def_sk_dict.get('k', 10)))
            }
            if search_type == 'mmr':
                search_kwargs['fetch_k'] = int(sk.get('fetch_k', def_sk_dict.get('fetch_k', 20)))
                search_kwargs['lambda_mult'] = float(sk.get('lambda_mult', def_sk_dict.get('lambda_mult', 0.5)))
            if search_type == 'similarity_score_threshold':
                search_kwargs['score_threshold'] = float(sk.get('score_threshold', def_sk_dict.get('score_threshold', 0.5)))
            return GVDBsCfgJSON(search_type, search_kwargs)
        except Exception:
            return GVDBsCfgJSON(**DEFAULT_dicts[DEFAULT_SEARCH_TYPE])
