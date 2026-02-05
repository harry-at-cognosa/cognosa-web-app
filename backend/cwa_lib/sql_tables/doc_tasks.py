import json
from traceback import format_exc
from sqlalchemy import select, delete
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import GroupVDBs, GroupLLMs, DocTasks
from common.sql_models.doc_tasks import get_short_name
from cwa_lib.pydantic_schemas.doc_tasks import DocTaskQueryShort, DocTaskQueryShortItem, DocTaskQueryResult
from common.enums.doc_task_status import TaskStatus


class DocTasksTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def row_as_json(row_obj) -> str:
        ignore_columns = ("deleted",
            "gllms_status", "gllms_status_updated_at", "gllms_created_at", "gllms_status_text",
            "gvdbs_status", "gvdbs_status_updated_at", "gvdbs_created_at", "gvdbs_status_text"
        )
        return json.dumps({k: v for k, v in row_obj.__dict__.items() 
                           if not (k.startswith('_') or k in ignore_columns)
                           }, indent=1, default=str)

    async def query_gvdbs(self, group_id: int, gvdbs_id: int):
        result = await self.session.execute(
            select(GroupVDBs)
            .where(
                (GroupVDBs.group_id == group_id) 
                & 
                (GroupVDBs.gvdbs_id == gvdbs_id)
                & 
                (GroupVDBs.deleted == 0)
                & 
                (GroupVDBs.enabled == True)
            )
            )
        return result.scalar_one_or_none()
    
    async def query_gllms(self, group_id: int, gllms_id: int):
        result = await self.session.execute(
            select(GroupLLMs)
            .where(
                (GroupLLMs.group_id == group_id) 
                & 
                (GroupLLMs.gllms_id == gllms_id)
                & 
                (GroupLLMs.deleted == 0)
                &
                (GroupLLMs.enabled == True)
            )
            )
        return result.scalar_one_or_none()

    async def short_query_all_by_group_id_user_id(self, group_id: int, user_id: int) -> DocTaskQueryShort:
        result = await self.session.execute(
            select(DocTasks)
            .where(
                (DocTasks.group_id == group_id) & (DocTasks.user_id == user_id)
            )
            .order_by(DocTasks.created_at.desc())
            .limit(100)
        )        
            
        rows = result.scalars().all()
        return DocTaskQueryShort(rows=[
            DocTaskQueryShortItem(
                doc_task_id=row.doc_task_id,
                status=row.status,
                status_text=row.status_text,
                created_at=row.created_at,
                short_name=get_short_name(row),
                is_processing=row.status not in TaskStatus.FINISHED_LIST,
                is_error=row.status in TaskStatus.ERROR_LIST,
                status_pct=TaskStatus.get_pct(row.status),
            ) for row in rows
        ])
    
    async def get_gvdbs_gllms_json(self, group_id: int, gvdbs_id: int, gllms_id: int)-> tuple[str, str]:
        # get group_vdbs and group_llms rows
        gvdbs_json = '{}'
        if gvdbs_id != -1:  # -1 means no document search
            if not (gvdbs_obj := await self.query_gvdbs(group_id, gvdbs_id)):
                error_msg = 'DocTasksTable.add_one: group_vdbs row not found for {group_id=}, {gvdbs_id=}'
                log.error(error_msg)
                raise Exception(error_msg)
            gvdbs_json = self.row_as_json(gvdbs_obj)
        
        if not (gllms_obj := await self.query_gllms(group_id, gllms_id)):
            error_msg = 'DocTasksTable.add_one: group_llms row not found for {group_id=}, {gllms_id=}'
            log.error(error_msg)
            raise Exception(error_msg)
        gllms_json = self.row_as_json(gllms_obj)
        return gvdbs_json, gllms_json
    
    async def add_one(
            self, 
            group_id: int, 
            user_id: int,
            gvdbs_id: int,
            gvdbs_cfg_json: str,
            gllms_id: int,
            gc_id: int, 
            short_name: str, 
            input_text: str, 
            optional_text: str) -> DocTaskQueryResult | None:
        # get group_vdbs and group_llms rows
        gvdbs_json, gllms_json = await self.get_gvdbs_gllms_json(group_id, gvdbs_id, gllms_id)
        
        task = DocTasks(
            group_id=group_id, 
            user_id=user_id, 
            gvdbs_id=gvdbs_id,
            gvdbs_cfg_json=gvdbs_cfg_json,
            gvdbs_json=gvdbs_json,
            gllms_id=gllms_id,
            gllms_json=gllms_json,
            gc_id=gc_id,
            short_name=short_name, 
            input_text=input_text, 
            optional_text=optional_text,
            status=TaskStatus.QD_INIT,
            status_text="Task placed..."
        )
        try:
            self.session.add(task)
            await self.session.commit()
            return DocTaskQueryResult(
                **task.__dict__,
                is_processing = True,
                is_error = False,
                status_pct=0,
            )
        except Exception:
            log.debug(f"Can't add new doc_tasks row for {group_id=}, {user_id=}, {gvdbs_id=}, {gllms_id=}, {gc_id=}, {short_name=}\n"
                      f"{input_text=}\n"
                      f"{optional_text=}\n"
                      f"Exception:\n{format_exc()}")
            return None
        
    async def add_second(
            self, 
            doc_task_id: int,
            user_group_id: int, 
            gvdbs_id: int,
            gvdbs_cfg_json: str,
            gllms_id: int,
            gc_id: int, 
            short_name: str, 
            input_text: str, 
            optional_text: str) -> DocTaskQueryResult | None:
        # get group_vdbs and group_llms rows
        gvdbs_json, gllms_json = await self.get_gvdbs_gllms_json(user_group_id, gvdbs_id, gllms_id)
        where_clause = (DocTasks.doc_task_id==doc_task_id) & (DocTasks.group_id == user_group_id)
        result = await self.session.execute(select(DocTasks).where(where_clause))
        task = result.scalar_one_or_none()
        if not task:
            return None
        if task.question_number > 1:
            raise Exception("Task already has follow-up question")
        
        task.gvdbs_id = gvdbs_id
        task.gvdbs_cfg_json=gvdbs_cfg_json
        task.gvdbs_json=gvdbs_json
        task.gllms_id=gllms_id
        task.gllms_json=gllms_json
        task.gc_id=gc_id
        task.short_name=short_name
        task.input_text=input_text
        task.optional_text=optional_text
        task.status=TaskStatus.QD_INIT
        task.status_text="Task placed..."
        task.question_number += 1
        try:
            await self.session.commit()
            await self.session.refresh(task)
            return DocTaskQueryResult(
                **task.__dict__,
                is_processing = True,
                is_error = False,
                status_pct=0,
            )
        except Exception:
            log.debug(f"Can't add new doc_tasks row for {user_group_id=}, {gvdbs_id=}, {gllms_id=}, {gc_id=}, {short_name=}\n"
                      f"{input_text=}\n"
                      f"{optional_text=}\n"
                      f"Exception:\n{format_exc()}")
            return None

    async def query_one_by_doc_task_id(self, doc_task_id: int) -> DocTaskQueryResult | None:
        result = await self.session.execute(
            select(DocTasks)
            .where(
                DocTasks.doc_task_id == doc_task_id
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None

        return DocTaskQueryResult(
            **row.__dict__, 
            is_processing=row.status not in TaskStatus.FINISHED_LIST,
            is_error=row.status in TaskStatus.ERROR_LIST,
            status_pct=TaskStatus.get_pct(row.status),
        )

    async def delete_one_by_doc_task_id_group_id(self, doc_task_id: int, group_id: int | None) -> bool:
        """
        Delete one row by doc_task_id and group_id. If group_id is None, don't use it.
        """
        if group_id is None:
            where_clause = DocTasks.doc_task_id == doc_task_id
        else:
            where_clause = (DocTasks.doc_task_id == doc_task_id) & (DocTasks.group_id == group_id)
        result = await self.session.execute(
            delete(DocTasks)
            .where(where_clause)
        )
        await self.session.commit()
        return bool(result.rowcount)
