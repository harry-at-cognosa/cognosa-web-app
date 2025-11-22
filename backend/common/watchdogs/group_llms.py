from sqlalchemy import func, select, update
from common.sql_db_async import AsyncSession
from common.sql_db_sync import Session
from common.sql_models import GroupLLMs


class GroupLLMsTable:
    def __init__(self) -> None:
        pass

    @classmethod
    async def async_select_by_group_id_order_by_seqn(cls, session: AsyncSession, group_id: int) -> list[GroupLLMs]:
        where_clause = (GroupLLMs.deleted == 0) & (GroupLLMs.group_id == group_id)
        stmt = select(GroupLLMs).where(where_clause).order_by(GroupLLMs.gllms_seqn)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def async_select_all_order_by_group_id_seqn(cls, session: AsyncSession) -> list[GroupLLMs]:
        stmt = select(GroupLLMs).where(GroupLLMs.deleted==0).order_by(GroupLLMs.group_id, GroupLLMs.gllms_seqn)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @classmethod
    def sync_select_all(cls, session: Session) -> list[GroupLLMs]:
        stmt = select(GroupLLMs).where(GroupLLMs.deleted==0).order_by(GroupLLMs.gllms_id)
        return list(session.execute(stmt).scalars().all())
    
    @classmethod
    def sync_update_gllms_status(
        cls,
        session: Session,
        gllms_id: int,
        gllms_status: str,
        gllms_status_text: str,
    ) -> None:
        stmt = (
            update(GroupLLMs)
            .where(GroupLLMs.gllms_id == gllms_id)
            .values(
                gllms_status=gllms_status, 
                gllms_status_text=gllms_status_text,
                gllms_status_updated_at=func.now()
                )
            )
        session.execute(stmt)
        session.commit()
