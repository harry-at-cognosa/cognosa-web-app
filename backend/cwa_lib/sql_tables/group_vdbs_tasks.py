from sqlalchemy.dialects.postgresql import insert
from common.sql_db_async import AsyncSession
from common.sql_models import GroupVDBsTasks


class GroupVDBsTasksTable:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def replace(self, gvdbs_id: int, gvt_type: int, gvt_status: int):
        """
        Replace one row - insert or update if (gvdbs_id, gvt_type) already exists
        """
        stmt = insert(GroupVDBsTasks).values(
            gvdbs_id=gvdbs_id,
            gvt_type=gvt_type,
            gvt_status=gvt_status
        ).on_conflict_do_update(  # PostgreSQL specific
            index_elements=['gvdbs_id', 'gvt_type'],  # The unique constraint columns
            set_=dict(gvt_status=gvt_status)  # Update status if conflict occurs
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
