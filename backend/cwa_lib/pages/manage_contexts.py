from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import GroupContexts
from common.sql_tools import create_order_clause
from sqlalchemy import select
from cwa_lib.pydantic_schemas.generic_table import ColumnType, TableOptions, TableQuery, TableDeleteRowResult
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
    create__allow=True,
    update__allow=True,
    delete__allow=True,
    delete__ask_columns=['gc_name'],
    order_by__allow=['gc_seqn', 'gc_name', 'gc_text']
)


class ManageContextsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all_by_group_id(
            self,
            group_id: int,
            payload: TableQuery,
            deleted: int | None
            ) -> ManageContextsQueryResult:
        where_clause = GroupContexts.group_id == group_id
        if deleted is not None:
            where_clause &= GroupContexts.deleted == deleted
        order_clause = create_order_clause(GroupContexts, manage_contexts__table_options.pk, payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(GroupContexts)
            .where(where_clause)
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
    
    async def mark_deleted_by_group_id_gc_id(self, group_id: int | None, gc_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by group_id and gc_id.
        If group_id is None, only by gc_id.
        """
        where_clause = GroupContexts.gc_id == gc_id
        if group_id is not None:
            where_clause &= GroupContexts.group_id == group_id
        try:
            result = await self.session.execute(select(GroupContexts).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            await self.session.commit()
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in ManageContextsTable.delete_by_group_id_gc_id ({group_id=}, {gc_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
