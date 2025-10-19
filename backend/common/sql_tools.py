from dataclasses import dataclass
from sqlalchemy import asc, desc, text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase
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
    default_order_by: str,
    order_by: str | None,
    order_dir: Literal['asc', 'desc'] | None
) -> tuple[ColumnElement, str, Literal['asc', 'desc']]:
    """
    Create safe order clause to use in .order_by(...)
    """
    # default order_dir is asc
    order_by = order_by if order_by else default_order_by
    order_func, order_dir = (desc, 'desc') if (order_dir == 'desc') else (asc, 'asc')
    column = getattr(model, order_by)
    return order_func(column), order_by, order_dir

###
#  Table info: table name, pk column name, `..._seqn` column name
###
@dataclass
class TableInfo:
    table_name: str
    pk_col: str
    seqn_col: str

def get_table_info(model: type[DeclarativeBase]) -> TableInfo:
    """
    Given a SQLAlchemy model class, returns a TableInfo dataclass containing:
    - table_name: the name of the database table
    - pk_col: the name of the single primary key column
    - seqn_col: the name of the column ending with '_seqn'
    """
    table_name = model.__tablename__
    mapper = inspect(model)
    pk_columns = [col.name for col in mapper.primary_key]
    if len(pk_columns) != 1:
        raise ValueError(f"Expected exactly one primary key column, got {len(pk_columns)}")
    pk_col = pk_columns[0]
    # find _seqn col. It should be e.g. `gc_seqn` for `pk gc_id`
    prefix = pk_col.replace('_id', '')
    expected_seqn_col = f"{prefix}_seqn"
    seqn_cols = [col.name for col in mapper.columns if col.name.endswith('_seqn')]
    seqn_col = seqn_cols[0]
    if seqn_col != expected_seqn_col:
        raise ValueError(f"{expected_seqn_col=}, {seqn_col=}")

    return TableInfo(table_name=table_name, pk_col=pk_col, seqn_col=seqn_col)

###
#  Resequence for the same group_id
###
async def async_reseqn_by_group_id(
            session: AsyncSession, 
            model: type[DeclarativeBase],
            group_id: int, 
            prioritize_pk: int,
            only_non_deleted: bool = True,
            commit: bool = True
        ) -> None:
        """
        Resequence e.g. `gc_seqn` for all rows of a given group_id,
        starting from 1 and incrementing by 1, ordered by (e.g. `gc_seqn` ASC, `gc_id` DESC).
        """
        ti = get_table_info(model)
        table_name, pk_col, seqn_col = (ti.table_name, ti.pk_col, ti.seqn_col)
        non_deleted_where_str = 'deleted = 0' if only_non_deleted else '(TRUE)'
        query = text(f"""
            UPDATE {table_name}
            SET {seqn_col} = sub.new_seqn
            FROM (
                SELECT 
                    {pk_col},
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            {seqn_col} ASC,
                            ({pk_col} = :prioritize_pk) DESC,
                            {pk_col} DESC
                    ) AS new_seqn
                FROM {table_name}
                WHERE group_id = :group_id AND {non_deleted_where_str}
            ) AS sub
            WHERE {table_name}.{pk_col} = sub.{pk_col};
        """)
        
        await session.execute(query, {"group_id": group_id, "prioritize_pk": prioritize_pk or 0})
        if commit:
            await session.commit()
