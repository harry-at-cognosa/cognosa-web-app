import json
from typing import Literal, TypeGuard

TYPE__SEARCH_TYPE = Literal['similarity', 'mmr', 'similarity_score_threshold']
TYPE__SEARCH_KWARGS = dict[Literal['k', 'fetch_k', 'lambda_mult', 'score_threshold'], int | float]
TYPE__SEARCH_KWARGS__SIM = dict[Literal['k'], int]
TYPE__SEARCH_KWARGS__MMR = dict[Literal['k', 'fetch_k', 'lambda_mult'], int | float]
TYPE__SEARCH_KWARGS__SST = dict[Literal['k', 'score_threshold'], int | float]

ALLOWED_SEARCH_TYPES = ['similarity', 'mmr', 'similarity_score_threshold']
def is_valid_search_type(value: str) -> TypeGuard[TYPE__SEARCH_TYPE]:
    return value in ALLOWED_SEARCH_TYPES

DEFAULT_SEARCH_TYPE = 'similarity'
DEFAULT_RETR_PARAMS = {
    'search_type': DEFAULT_SEARCH_TYPE, 
    'search_kwargs__similarity': {'k': 10},
    'search_kwargs__mmr': {'k': 10, 'fetch_k': 20, 'lambda_mult': 0.5},
    'search_kwargs__similarity_score_threshold': {'k': 10, 'score_threshold': 0.5}
}


class ValidateSearchKwargs:
    @staticmethod
    def validate_pos_int(name: str, value: str | float | int) -> int:
        try:
            value = int(value)
            if value <= 0:
                raise Exception
            return value
        except Exception:
            raise ValueError(f"Wrong {name}") from None

    @staticmethod
    def validate_float(name: str, value: str | float | int) -> float:
        try:
            return float(value)
        except Exception:
            raise ValueError(f"Wrong {name}") from None

    @classmethod
    def k(cls, value: str | float | int) -> int:
        return cls.validate_pos_int('k', value)
    @classmethod
    def fetch_k(cls, value: str | float | int) -> int:
        return cls.validate_pos_int('fetch_k', value)
    @classmethod
    def lambda_mult(cls, value: str | float | int) -> float:
        return cls.validate_float('lambda_mult', value)
    @classmethod
    def score_threshold(cls, value: str | float | int) -> float:
        return cls.validate_float('score_threshold', value)


class GVDBsRetrParams:
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
    def __init__(self, search_type: TYPE__SEARCH_TYPE, search_kwargs: TYPE__SEARCH_KWARGS):
        self.search_type: TYPE__SEARCH_TYPE = search_type
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

    @classmethod
    def from_dict(cls, gvdbs_retr_params: str | dict) -> 'GVDBsRetrParams':
        try:
            cfg_dict = gvdbs_retr_params if isinstance(gvdbs_retr_params, dict) else json.loads(gvdbs_retr_params)
            # search_type
            search_type: TYPE__SEARCH_TYPE = cfg_dict.get('search_type', DEFAULT_SEARCH_TYPE)
            if not(is_valid_search_type(search_type)):
                raise Exception            
            # search_kwargs
            sk: dict = dict(cfg_dict.get('search_kwargs', dict()))
            def_sk_dict = DEFAULT_RETR_PARAMS.get('search_kwargs__' + search_type, dict())
            search_kwargs: TYPE__SEARCH_KWARGS = {
                'k': ValidateSearchKwargs.k(sk.get('k', def_sk_dict.get('k', 10)))
            }
            if search_type == 'mmr':
                search_kwargs['fetch_k'] = ValidateSearchKwargs.fetch_k(
                    sk.get('fetch_k', def_sk_dict.get('fetch_k', 20))
                )
                search_kwargs['lambda_mult'] = ValidateSearchKwargs.lambda_mult(
                    sk.get('lambda_mult', def_sk_dict.get('lambda_mult', 0.5))
                )
            if search_type == 'similarity_score_threshold':
                search_kwargs['score_threshold'] = ValidateSearchKwargs.score_threshold(
                    sk.get('score_threshold', def_sk_dict.get('score_threshold', 0.5))
                )
            return cls(search_type, search_kwargs)
        except Exception:
            return cls(DEFAULT_SEARCH_TYPE, **DEFAULT_RETR_PARAMS[DEFAULT_SEARCH_TYPE])

class GVDBsDefRetrParams:
    def __init__(
            self, 
            search_type: TYPE__SEARCH_TYPE,
            search_kwargs__similarity: TYPE__SEARCH_KWARGS__SIM,
            search_kwargs__mmr: TYPE__SEARCH_KWARGS__MMR,
            search_kwargs__similarity_score_threshold: TYPE__SEARCH_KWARGS__SST
            ):
        self.search_type = search_type
        self.search_kwargs__similarity = search_kwargs__similarity
        self.search_kwargs__mmr = search_kwargs__mmr
        self.search_kwargs__similarity_score_threshold = search_kwargs__similarity_score_threshold

    @classmethod
    def from_dict(cls, gvdbs_def_retr_params: str | dict) -> 'GVDBsDefRetrParams':
        try:
            cfg_dict = gvdbs_def_retr_params if isinstance(gvdbs_def_retr_params, dict) else json.loads(gvdbs_def_retr_params)
            # search_type
            search_type: TYPE__SEARCH_TYPE = cfg_dict['search_type']
            if not(is_valid_search_type(search_type)):
                raise Exception            
            # search_kwargs
            sk__sim: TYPE__SEARCH_KWARGS__SIM = dict(cfg_dict['search_kwargs__similarity'])
            sk__mmr: TYPE__SEARCH_KWARGS__MMR = dict(cfg_dict['search_kwargs__mmr'])
            sk__sst: TYPE__SEARCH_KWARGS__SST = dict(cfg_dict['search_kwargs__similarity_score_threshold'])
            new_dict = {
                'search_type': search_type,
                'search_kwargs__similarity': {
                    'k': ValidateSearchKwargs.k(sk__sim['k'])
                },
                'search_kwargs__mmr': {
                    'k': ValidateSearchKwargs.k(sk__mmr['k']),
                    'fetch_k': ValidateSearchKwargs.fetch_k(sk__mmr['fetch_k']),
                    'lambda_mult': ValidateSearchKwargs.lambda_mult(sk__mmr['lambda_mult']),
                },
                'search_kwargs__similarity_score_threshold': {
                    'k': ValidateSearchKwargs.k(sk__sst['k']),
                    'score_threshold': ValidateSearchKwargs.score_threshold(sk__sst['score_threshold'])
                }
            }
            return cls(**new_dict)
        except Exception:
            raise ValueError from None

    def as_dict(self) -> dict:
        return {
            'search_type': self.search_type,
            'search_kwargs__similarity': self.search_kwargs__similarity,
            'search_kwargs__mmr': self.search_kwargs__mmr,
            'search_kwargs__similarity_score_threshold': self.search_kwargs__similarity_score_threshold
        }

    @classmethod
    def from_obsolete_gvdbs_cfg(cls, gvdbs_cfg: str | dict) -> 'GVDBsDefRetrParams':
        try:
            d: dict = json.loads(gvdbs_cfg) if isinstance(gvdbs_cfg, str) else gvdbs_cfg
            search_type = str(d['search_type'])
            if not(is_valid_search_type(search_type)):
                raise Exception
            sk: dict[str, int | float] = dict(d['search_kwargs'])
            # make new search_kwargs__* dictionaries
            drp = DEFAULT_RETR_PARAMS['search_kwargs__similarity']
            k = ValidateSearchKwargs.k(sk.get('k', int(drp['k'])))
            sk_sim: TYPE__SEARCH_KWARGS__SIM = {'k': k}
            #
            drp = DEFAULT_RETR_PARAMS['search_kwargs__mmr']
            k = ValidateSearchKwargs.k(sk.get('k', int(drp['k'])))
            fetch_k = ValidateSearchKwargs.fetch_k(sk.get('fetch_k', int(drp['fetch_k'])))
            lambda_mult = ValidateSearchKwargs.lambda_mult(sk.get('lambda_mult', float(drp['lambda_mult'])))
            sk_mmr: TYPE__SEARCH_KWARGS__MMR = {'k': k, 'fetch_k': fetch_k, 'lambda_mult': lambda_mult}
            #
            drp = DEFAULT_RETR_PARAMS['search_kwargs__similarity_score_threshold']
            k = ValidateSearchKwargs.k(sk.get('k', int(drp['k'])))
            score_threshold = ValidateSearchKwargs.score_threshold(sk.get('score_threshold', float(drp['score_threshold'])))
            sk_sst: TYPE__SEARCH_KWARGS__SST = {'k': k, 'score_threshold': score_threshold}
            return cls(
                search_type=search_type, 
                search_kwargs__similarity=sk_sim, 
                search_kwargs__mmr=sk_mmr, 
                search_kwargs__similarity_score_threshold=sk_sst
            )
        except Exception:
            return cls(**DEFAULT_RETR_PARAMS)
