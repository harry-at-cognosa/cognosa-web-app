from sqlalchemy import asc, desc
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.elements import ColumnElement
from typing import Literal, Type, TypeVar


Base = declarative_base()

from .patch_sqlalchemy import utcnow
from .api_settings import ApiSettings
from .api_groups import ApiGroups
from .api_users import User
from .group_contexts import GroupContexts
from .group_vdbs import GroupVDBs
from .group_llm import GroupLLMs
from .doc_tasks import DocTasks
from .api_processes import ApiProcesses


T = TypeVar('T')
def create_order_clause(
    model: Type[T], 
    pk: str,
    order_by: str | None, 
    order_dir: Literal['asc', 'desc'] | None
) -> ColumnElement:
    """
    Create safe order clause to use in .order_by(...)
    """
    # default order_dir is asc
    order_func = desc if (order_dir == 'desc') else asc
    column = getattr(model, order_by if order_by else pk)
    return order_func(column)
