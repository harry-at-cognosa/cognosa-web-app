from pydantic import BaseModel
from .gvdbs_retr_params import TYPE__SEARCH_TYPE, TYPE__SEARCH_KWARGS
from .gvdbs_retr_filters import RequestGVDBsRetrFilters


class GVDBsCfgJSON(BaseModel):
    search_type: TYPE__SEARCH_TYPE
    search_kwargs: TYPE__SEARCH_KWARGS
    filters: RequestGVDBsRetrFilters | None = None
