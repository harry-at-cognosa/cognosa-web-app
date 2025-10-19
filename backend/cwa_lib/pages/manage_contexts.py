from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import GroupContexts
from common.sql_tools import create_order_clause
from sqlalchemy import select, update, text
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.manage_contexts import ManageContextsQueryResult, ManageContextsCreate, ManageContextsUpdate

default_gc_text = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}
Helpful Answer:
"""


manage_contexts__query_columns = {
    'gc_id': ColumnType(display='ID', type='number'),
    'group_id': ColumnType(display='Group ID', type='number'),
    'gc_seqn': ColumnType(display='Seqn #', type='number', default=0),
    'gc_name': ColumnType(display='Name', type='string', default="New context"),
    'gc_text': ColumnType(display='Text', type='text', default=default_gc_text),
}

manage_contexts__table_options = TableOptions(
    title='Group Contexts',
    pk='gc_id',
    read__visible_columns=['gc_seqn', 'gc_name', 'gc_text'],
    create__ask_columns=['gc_seqn', 'gc_name', 'gc_text'],
    update__ask_columns=['gc_seqn', 'gc_name', 'gc_text'],
    delete__ask_columns=['gc_name'],
    order_by__allow=['gc_seqn', 'gc_name']
)


class ManageContextsTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def fix_gc_text(self, gc_text: str) -> str:
        if '{context}' not in gc_text:
            gc_text += "\nContext:\n{context}\n"
        if '{question}' not in gc_text:
            gc_text += "\nQuestion: {question}\n"
        return gc_text

    async def resequence_group_contexts(
            self, 
            group_id: int, 
            prioritize_gc_id: int,
            commit: bool = False
        ) -> None:
        """
        Resequence gc_seqn for all non-deleted GroupContexts of a given group_id,
        starting from 1 and incrementing by 1, ordered by (gc_seqn ASC, gc_id DESC).
        
        Only affects rows where `deleted = 0`.
        """
        query = text("""
            UPDATE group_contexts
            SET gc_seqn = sub.new_seqn
            FROM (
                SELECT 
                    gc_id,
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            gc_seqn ASC,
                            (gc_id = :prioritize_gc_id) DESC,
                            gc_id DESC
                    ) AS new_seqn
                FROM group_contexts
                WHERE group_id = :group_id AND deleted = 0
            ) AS sub
            WHERE group_contexts.gc_id = sub.gc_id;
        """)
        
        await self.session.execute(query, {"group_id": group_id, "prioritize_gc_id": prioritize_gc_id or 0})
        if commit:
            await self.session.commit()

    async def query_all_by_group_id(
            self,
            group_id: int,
            payload: TableQuery,
            deleted: int | None
            ) -> ManageContextsQueryResult:
        where_clause = GroupContexts.group_id == group_id
        if deleted is not None:
            where_clause &= GroupContexts.deleted == deleted
        order_clause, order_by, order_dir = create_order_clause(GroupContexts, 'gc_seqn', payload.order_by, payload.order_dir)
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
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def create_one(self, group_id: int, data: ManageContextsCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        gc_seqn__default = manage_contexts__query_columns['gc_seqn'].default
        gc_name__default = manage_contexts__query_columns['gc_name'].default
        new_row = GroupContexts(
            group_id=group_id,
            gc_seqn=data.gc_seqn if (data.gc_seqn is not None) else gc_seqn__default,
            gc_name=data.gc_name if data.gc_name else gc_name__default,
            gc_text=self.fix_gc_text(data.gc_text)
        )
        self.session.add(new_row)
        await self.session.commit()
        await self.session.refresh(new_row)
        await self.resequence_group_contexts(group_id, prioritize_gc_id=new_row.gc_id, commit=True)
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, group_id: int, data: ManageContextsUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        update_values = dict()
        if data.gc_name:
            update_values['gc_name'] = data.gc_name.strip()
        if data.gc_text:
            update_values['gc_text'] = self.fix_gc_text(data.gc_text).strip()
        if data.gc_seqn is not None:
            update_values['gc_seqn'] = data.gc_seqn

        if not update_values:
            # Nothing to update
            return TableUpdateRowResult(result='success', total_updated=0)

        where_clause = (GroupContexts.gc_id == data.gc_id) & (GroupContexts.group_id == group_id)
        stmt = (
            update(GroupContexts)
            .where(where_clause)
            .values(**update_values)
        )
        result = await self.session.execute(stmt)
        total_updated = result.rowcount
        await self.session.commit()
        if (total_updated > 0) and ('gc_seqn' in update_values):
            await self.resequence_group_contexts(group_id, prioritize_gc_id=data.gc_id, commit=True)
        return TableUpdateRowResult(result='success', total_updated=total_updated)

    
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
            await self.resequence_group_contexts(row.group_id, prioritize_gc_id=0, commit=True)
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in ManageContextsTable.delete_by_group_id_gc_id ({group_id=}, {gc_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
