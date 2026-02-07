from sqlalchemy import select
from common.sql_db_async import AsyncSession
from common.sql_models import GroupVDBsSelectValues


class GroupVDBsSelectValuesTable:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_path__values(self, gvdbs_id: int) -> dict[str, list[str]]:
        """
        Get rows by gvdbs_id. Group by path.
        """
        stmt = select(GroupVDBsSelectValues).where(GroupVDBsSelectValues.gvdbs_id==gvdbs_id).order_by(GroupVDBsSelectValues.gvsv_id)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        d: dict[str, list[str]] = dict()
        for row in rows:
            d.setdefault(row.gvsv_path, []).append(row.gvsv_value)
        return d
