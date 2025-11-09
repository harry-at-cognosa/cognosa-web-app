from typing import Sequence
from sqlalchemy import select
from common.enums.gvdbs_cfg_json import DEFAULT_SEARCH_TYPE, DEFAULT_dicts
from common.sql_db_async import AsyncSession
from common.sql_models import User, GroupContexts, GroupLLMs, GroupVDBs
from cwa_lib.pydantic_schemas.doc_tasks import (
    DocTaskOptionsResult, 
    DocTasksOptionsGroupContextsRow, 
    DocTasksOptionsGroupLLMsRow, 
    DocTasksOptionsGroupVDBsRow,
    GVDBsCfgDefaults
)


class QueryDocumentsOptions:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def _from__group_contexts(self) -> Sequence[DocTasksOptionsGroupContextsRow]:
        where_clause = (GroupContexts.group_id == self.user.group_id) & (GroupContexts.deleted == 0)
        result = await self.session.execute(select(GroupContexts).where(where_clause).order_by(GroupContexts.gc_seqn))
        return result.scalars().all()
    
    async def _from__group_llms(self) -> Sequence[DocTasksOptionsGroupLLMsRow]:
        where_clause = (GroupLLMs.group_id == self.user.group_id) & (GroupLLMs.deleted == 0)
        result = await self.session.execute(select(GroupLLMs).where(where_clause).order_by(GroupLLMs.gllms_id))
        return result.scalars().all()
    
    async def _from__group_vdbs(self) -> Sequence[DocTasksOptionsGroupVDBsRow]:
        where_clause = (GroupVDBs.group_id == self.user.group_id) & (GroupVDBs.deleted == 0)
        result = await self.session.execute(select(GroupVDBs).where(where_clause).order_by(GroupVDBs.gvdbs_id))
        return result.scalars().all()

    async def get_options(self) -> DocTaskOptionsResult:
        """
        Get options for Query Documents from tables:
            1) `group_contexts`
            2) `group_llms`
            3) `group_vdbs`
        Also:
        `gvdbs_cfg_defaults`: default values for `doc_tasks.gvdbs_cfg_json`.
        """
        return DocTaskOptionsResult(
            group_contexts=await self._from__group_contexts(),
            group_llms=await self._from__group_llms(),
            group_vdbs=await self._from__group_vdbs(),
            gvdbs_cfg_defaults=GVDBsCfgDefaults(search_type=DEFAULT_SEARCH_TYPE, search_kwargs_per_type=DEFAULT_dicts)
        )
