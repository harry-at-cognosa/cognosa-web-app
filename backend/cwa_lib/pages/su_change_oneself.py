from common import log
from common.sql_db_async import AsyncSession
from common.sql_models.api_users import User
from cwa_lib.pydantic_schemas.su_change_oneself import (
    SuChangeOneselfGroup, SuChangeOneselfGetResult, SuChangeOneselfUpdate, SuChangeOneselfUpdateResult
)
from cwa_lib.sql_tables.api_groups import ApiGroupsTable


class SuChangeOneselfPage:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def get_options(self):
        group_rows = await ApiGroupsTable(self.session).get_all_not_deleted()
        return SuChangeOneselfGetResult(
            group_id=self.user.group_id,
            group_list=[SuChangeOneselfGroup(
                group_id=row.group_id, 
                group_name=row.group_name,
            ) for row in group_rows],
            is_groupadmin=self.user.is_groupadmin,
            is_contentmanager=self.user.is_contentmanager,
        )

    async def update(self, payload: SuChangeOneselfUpdate) -> SuChangeOneselfUpdateResult:
        target_group = await ApiGroupsTable(self.session).get_group_by_group_id(payload.group_id)
        if not target_group:
            return SuChangeOneselfUpdateResult(is_success=False, error_msg='No target group found')
        if target_group.deleted:
            return SuChangeOneselfUpdateResult(is_success=False, error_msg='Target group was deleted')
        try:
            self.user.is_contentmanager = payload.is_contentmanager
            self.user.is_groupadmin = payload.is_groupadmin
            self.user.group_id = payload.group_id
            await self.session.commit()
            await self.session.refresh(self.user)
            return SuChangeOneselfUpdateResult(
                is_success=True, 
                group_id=self.user.group_id,
                is_groupadmin=self.user.is_groupadmin,
                is_content_manager=self.user.is_contentmanager
            )
        except Exception as exc:
            await self.session.rollback()
            error_msg = f"Undefined Exception in SuChangeOneself:\n{exc}"
            log.error(error_msg)
            return SuChangeOneselfUpdateResult(is_success=False, error_msg=error_msg)
