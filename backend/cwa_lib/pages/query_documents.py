from typing import Sequence
from sqlalchemy import select
from common.features.gvdbs_retr_params import GVDBsRetrParams
from common.sql_db_async import AsyncSession
from common.sql_models import User, GroupContexts, GroupLLMs, GroupVDBs
from cwa_lib.pydantic_schemas.doc_tasks import (
    DocTaskCreate,
    DocTaskQueryResult,
    DocTaskOptionsResult, 
    DocTasksOptionsGroupContextsRow, 
    DocTasksOptionsGroupLLMsRow, 
    DocTasksOptionsGroupVDBsRow,
)
from cwa_lib.sql_tables.doc_tasks import DocTasksTable


class QueryDocumentsPage:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def create_task(self, payload: DocTaskCreate) -> DocTaskQueryResult | str:
        # check if VDBs and LLMs are ready (status != 'danger')
        if payload.gvdbs_id != -1:  # ignore "No Document search"
            gvdbs = await DocTasksTable(self.session).query_gvdbs(self.user.group_id, payload.gvdbs_id)
            if not (gvdbs and (gvdbs.gvdbs_status != 'danger')):
                return "Document collection is not ready"
        
        gllms = await DocTasksTable(self.session).query_gllms(self.user.group_id, payload.gllms_id)
        if not (gllms and (gllms.gllms_status != 'danger')):
            return "LLM is not ready"
        
        if not payload.doc_task_id:
            result = await DocTasksTable(self.session).add_one(
                group_id=self.user.group_id, 
                user_id=self.user.user_id, 
                gvdbs_id=payload.gvdbs_id,
                gvdbs_cfg_json=GVDBsRetrParams.from_dict(payload.gvdbs_cfg_json).as_dict(),
                gllms_id=payload.gllms_id,
                gc_id=payload.gc_id,
                short_name=payload.short_name, 
                input_text=payload.input_text, 
                optional_text=payload.optional_text
            )
        else:
            result = await DocTasksTable(self.session).add_second(
                doc_task_id=payload.doc_task_id,
                user_group_id=self.user.group_id,
                gvdbs_id=payload.gvdbs_id,
                gvdbs_cfg_json=GVDBsRetrParams.from_dict(payload.gvdbs_cfg_json).as_dict(),
                gllms_id=payload.gllms_id,
                gc_id=payload.gc_id,
                short_name=payload.short_name, 
                input_text=payload.input_text, 
                optional_text=payload.optional_text
            )
        if result is None:
            return "Cannot add new DocTask"
        return result

class QueryDocumentsOptions:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def _from__group_contexts(self) -> Sequence[DocTasksOptionsGroupContextsRow]:
        where_clause = (GroupContexts.group_id == self.user.group_id) & (GroupContexts.deleted == 0)
        result = await self.session.execute(select(GroupContexts).where(where_clause).order_by(GroupContexts.gc_seqn))
        return result.scalars().all()
    
    async def _from__group_llms(self) -> Sequence[DocTasksOptionsGroupLLMsRow]:
        where_clause = (GroupLLMs.group_id == self.user.group_id) & (GroupLLMs.deleted == 0) & (GroupLLMs.enabled == True)
        result = await self.session.execute(select(GroupLLMs).where(where_clause).order_by(GroupLLMs.gllms_id))
        return result.scalars().all()
    
    async def _from__group_vdbs(self) -> Sequence[DocTasksOptionsGroupVDBsRow]:
        where_clause = (GroupVDBs.group_id == self.user.group_id) & (GroupVDBs.deleted == 0) & (GroupVDBs.enabled == True)
        result = await self.session.execute(select(GroupVDBs).where(where_clause).order_by(GroupVDBs.gvdbs_id))
        return result.scalars().all()
    
    async def get_options(self) -> DocTaskOptionsResult:
        """
        Get options for Query Documents from tables:
            1) `group_contexts`
            2) `group_llms`
            3) `group_vdbs`
        """
        return DocTaskOptionsResult(
            group_contexts=await self._from__group_contexts(),
            group_llms=await self._from__group_llms(),
            group_vdbs=await self._from__group_vdbs(),
        )
