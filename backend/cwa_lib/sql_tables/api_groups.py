from typing import Sequence
from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import ApiGroups


class ApiGroupsTable:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_group_by_group_id(self, group_id: int) -> ApiGroups:
        result = await self.session.execute(select(ApiGroups).where(ApiGroups.group_id==group_id))
        return result.scalar_one_or_none()

    async def get_all_not_deleted(self) -> Sequence[ApiGroups]:
        result = await self.session.execute(select(ApiGroups).where(ApiGroups.deleted == 0).order_by(ApiGroups.group_id))
        return result.scalars().all()
