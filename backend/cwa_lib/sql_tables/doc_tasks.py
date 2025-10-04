from traceback import format_exc
from sqlalchemy import select, delete
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.doc_tasks import DocTasks
from cwa_lib.pydantic_schemas.doc_tasks import DocTaskQueryShort, DocTaskQueryShortItem, DocTaskQueryResult
from common.enums.doc_task_status import TaskStatus


class DocTasksTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
        def get_short_name(d: DocTasks) -> str:
            if d.short_name and d.short_name.strip():
                return d.short_name
            CHAR_LIMIT = 50
            input_text = d.input_text.strip()
            if len(input_text) > CHAR_LIMIT:
                return input_text[:CHAR_LIMIT] + '...'
            return input_text

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
    
    async def add_one(
            self, 
            group_id: int, 
            user_id: int,
            gvdbs_id: int,
            gllms_id: int,
            gc_id: int, 
            short_name: str, 
            input_text: str, 
            optional_text: str) -> DocTaskQueryResult | None:
        
        task = DocTasks(
            group_id=group_id, 
            user_id=user_id, 
            gvdbs_id=gvdbs_id,
            gllms_id=gllms_id,
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
            print(format_exc())
            log.debug(f"Can't add new doc_tasks row for {group_id=}, {user_id=}, {gvdbs_id=}, {gllms_id=}, {gc_id=}, {short_name=}\n"
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
