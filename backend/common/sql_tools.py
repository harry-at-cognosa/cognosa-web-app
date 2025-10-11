from sqlalchemy import asc, desc
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.types import DateTime
from typing import Literal, Type, TypeVar

###
# Allow utc now for default value
###
class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    if element and compiler and kw:  # for code inspection
        pass
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


###
#  Create order_by clause
###
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