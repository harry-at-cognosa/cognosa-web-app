from common.sql_db_async import AsyncSession
from common.sql_models import GroupContexts
from common.sql_tools import create_order_clause
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery
from cwa_lib.pydantic_schemas.manage_contexts import ManageContextsQueryResult


manage_contexts__query_columns = {
    'gc_id': ColumnType(display='ID', seqn=None, type='number'),
    'group_id': ColumnType(display='Group ID', seqn=None, type='number'),
    'gc_seqn': ColumnType(display='Seqn #', seqn=3, type='number'),
    'gc_name': ColumnType(display='Name', seqn=4, type='string'),
    'gc_text': ColumnType(display='Text', seqn=5, type='text'),
}

manage_contexts__table_options = TableOptions(
    title='Manage Contexts',
    pk='gc_id',
    allow_add=True,
    allow_update=True,
    allow_delete=True,
    allow_order_by=['gc_seqn', 'gc_name', 'gc_text']
)


class ManageContextsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all_by_group_id(
            self,
            group_id: int,
            payload: TableQuery
            ) -> ManageContextsQueryResult:
        order_clause = create_order_clause(GroupContexts, manage_contexts__table_options.pk, payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(GroupContexts)
            .where(GroupContexts.group_id == group_id)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        return ManageContextsQueryResult(
            name='manage_contexts',
            rows=rows,
            columns=manage_contexts__query_columns,
            table_options=manage_contexts__table_options,
            total=len(rows)
        )