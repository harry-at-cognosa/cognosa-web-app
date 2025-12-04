from sqlalchemy import func, select, update
from common.sql_db_async import AsyncSession
from common.sql_db_sync import Session
from common.sql_models import GroupVDBs


class GroupVDBSTable:
    def __init__(self) -> None:
        pass

    @classmethod
    async def async_select_by_group_id_order_by_seqn(cls, session: AsyncSession, group_id: int) -> list[GroupVDBs]:
        where_clause = (GroupVDBs.deleted == 0) & (GroupVDBs.enabled == True) & (GroupVDBs.group_id == group_id)
        stmt = select(GroupVDBs).where(where_clause).order_by(GroupVDBs.gvdbs_seqn)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def async_select_all_order_by_group_id_seqn(cls, session: AsyncSession) -> list[GroupVDBs]:
        where_clause = (GroupVDBs.deleted == 0) & (GroupVDBs.enabled == True)
        stmt = select(GroupVDBs).where(where_clause).order_by(GroupVDBs.group_id, GroupVDBs.gvdbs_seqn)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @classmethod
    def sync_select_all_enabled(cls, session: Session) -> list[GroupVDBs]:
        where_clause = (GroupVDBs.deleted == 0) & (GroupVDBs.enabled == True)
        stmt = select(GroupVDBs).where((where_clause) & (GroupVDBs.enabled==True)).order_by(GroupVDBs.gvdbs_id)
        return list(session.execute(stmt).scalars().all())
    
    @classmethod
    def sync_update_gvdbs_status(
        cls,
        session: Session,
        gvdbs_id: int,
        gvdbs_status: str,
        gvdbs_status_text: str,
    ) -> None:
        stmt = (
            update(GroupVDBs)
            .where(GroupVDBs.gvdbs_id == gvdbs_id)
            .values(
                gvdbs_status=gvdbs_status, 
                gvdbs_status_text=gvdbs_status_text,
                gvdbs_status_updated_at=func.now()
                )
            )
        session.execute(stmt)
        session.commit()
