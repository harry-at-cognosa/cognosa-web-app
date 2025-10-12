from typing import Sequence
from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import User, GroupContexts, GroupLLMs, GroupVDBs
from cwa_lib.pydantic_schemas.doc_tasks import (
    DocTaskOptionsResult, 
    DocTasksOptionsGroupContextsRow, 
    DocTasksOptionsGroupLLMsRow, 
    DocTasksOptionsGroupVDBsRow
)


class RAGDocumentsOptions:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def _from__group_contexts(self) -> Sequence[DocTasksOptionsGroupContextsRow]:
        where_clause = (GroupContexts.group_id == self.user.group_id) & (GroupContexts.deleted == 0)
        result = await self.session.execute(select(GroupContexts).where(where_clause))
        return result.scalars().all()
    
    async def _from__group_llms(self) -> Sequence[DocTasksOptionsGroupLLMsRow]:
        where_clause = (GroupLLMs.group_id == self.user.group_id) & (GroupLLMs.deleted == 0)
        result = await self.session.execute(select(GroupLLMs).where(where_clause))
        return result.scalars().all()
    
    async def _from__group_vdbs(self) -> Sequence[DocTasksOptionsGroupVDBsRow]:
        where_clause = (GroupVDBs.group_id == self.user.group_id) & (GroupVDBs.deleted == 0)
        result = await self.session.execute(select(GroupVDBs).where(where_clause))
        return result.scalars().all()

    async def get_options(self) -> DocTaskOptionsResult:
        """
        Get options for RAG Documents from tables:
            1) `group_contexts`
            2) `group_llms`
            3) `group_vdbs`
        """
        return DocTaskOptionsResult(
            group_contexts=await self._from__group_contexts(),
            group_llms=await self._from__group_llms(),
            group_vdbs=await self._from__group_vdbs(),
        )
