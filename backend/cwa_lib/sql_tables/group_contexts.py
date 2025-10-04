from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models.group_contexts import GroupContexts
from cwa_lib.pydantic_schemas.generic_table import ColumnType
from cwa_lib.pydantic_schemas.group_contexts import ManageContextsQueryResult

manage_contexts_query_columns = {
    'gc_id': ColumnType(display='ID', seqn=1, type='number'), 
    'group_id': ColumnType(display='Group ID', seqn=2, type='number'),
    'gc_seqn': ColumnType(display='Seqn #', seqn=3, type='number'),
    'gc_name': ColumnType(display='Name', seqn=4, type='string'),
    'gc_text': ColumnType(display='Text', seqn=5, type='text'),
    }

class ManageContextsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all_by_group_id(self, group_id: int) -> ManageContextsQueryResult:
        result = await self.session.execute(select(GroupContexts).where(GroupContexts.group_id == group_id))
        rows = result.scalars().all()
        return ManageContextsQueryResult(
            name='manage_contexts',
            rows=rows,
            columns=manage_contexts_query_columns,
            total=len(rows)
        )