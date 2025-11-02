from sqlalchemy import select
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from common.sql_tools import create_order_clause, fix_autoincrement
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.su_manage_users import SuManageUsersQueryResult, SuManageUsersCreate, SuManageUsersUpdate
from cwa_lib.pages import get_qc_to_with_group_id_name

from cwa_lib.sql_tables.api_users import ApiUsersTable
from cwa_lib.app import password_helper


su_manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name', default=1, select=[]),
    'user_name': ColumnType(display='User name', type='string'),
    'full_name': ColumnType(display='Full name', type='string'),
    'email': ColumnType(display='Email', type='string'),
    'password': ColumnType(display='New Password', type='groupadmin_user_password'),
    'is_active': ColumnType(display='Active', type='boolean'),
    'is_contentmanager': ColumnType(display='Content\nManager', type='boolean', default=False),
    'is_groupadmin': ColumnType(display='Group\nAdmin', type='boolean', default=False),
    'is_superuser': ColumnType(display='Super\nUser', type='boolean', default=False),
    'created_at': ColumnType(display='Created at', type='datetime'),
}
su_manage_users__all_columns = list(su_manage_users__query_columns.keys())
su_manage_users_edit_columns = [x for x in su_manage_users__all_columns if (x not in ('user_id', 'created_at'))]

su_manage_users__table_options = TableOptions(
    title='SU Manage Users',
    pk='user_id',
    read__visible_columns=[x for x in su_manage_users__all_columns if (x != 'password')],
    read__hide_on_false=['is_active', 'is_contentmanager', 'is_groupadmin', 'is_superuser'],  # table view: hide if false
    create__ask_columns=su_manage_users_edit_columns,
    update__ask_columns=su_manage_users_edit_columns,
    delete__ask_columns=['user_name', 'full_name', 'email'],
    order_by__allow=su_manage_users__all_columns,
)


class SuManageUsersTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            payload: TableQuery
            ) -> SuManageUsersQueryResult:
        order_clause, order_by, order_dir = create_order_clause(User, su_manage_users__table_options.pk, payload.order_by, payload.order_dir)
        result = await self.session.execute(
            select(User)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        # update list of `api_groups`.`group_id` and `api_groups`.`group_name`
        manage_users__qc, manage_users__to = await get_qc_to_with_group_id_name(
            self.session, su_manage_users__query_columns, su_manage_users__table_options
        )
        #
        rows = result.scalars().all()
        return SuManageUsersQueryResult(
            name='su_manage_users',
            rows=rows,
            columns=manage_users__qc,
            table_options=manage_users__to,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def create_one(self, data: SuManageUsersCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, User)
        # check if user exists with the same email or user_name
        result = await self.session.execute(select(User).where(User.email==data.email)) # type: ignore
        exists = result.scalar_one_or_none()
        if exists:
            return TableCreateRowResult(result='error', error_msg='This email already exists', total_created=0)
        result = await self.session.execute(select(User).where(User.user_name==data.user_name))
        exists = result.scalar_one_or_none()
        if exists:
            return TableCreateRowResult(result='error', error_msg='This user_name already exists', total_created=0)
        
        await ApiUsersTable().create_user(
            user_id=None,
            email=data.email,
            password=data.password,
            user_name=data.user_name,
            full_name=data.full_name,
            group_id=data.group_id,
            is_active=data.is_active,
            is_verified=True,
            is_groupadmin=data.is_groupadmin,
            is_contentmanager=data.is_contentmanager
        )
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, cur_user_id: int, data: SuManageUsersUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        # get existing row from `api_users`
        result = await self.session.execute(select(User).where(User.user_id == data.user_id))
        user = result.scalar_one_or_none()
        if not user:
            return TableUpdateRowResult(result='error', total_updated=0)
        # check if user exists with the same email or user_name
        if data.email != user.email:
            result = await self.session.execute(select(User).where(User.email==data.email)) # type: ignore
            exists = result.scalar_one_or_none()
            if exists:
                return TableUpdateRowResult(result='error', error_msg='This email already exists', total_updated=0)
        if data.user_name != user.user_name:
            result = await self.session.execute(select(User).where(User.user_name==data.user_name))
            exists = result.scalar_one_or_none()
            if exists:
                return TableUpdateRowResult(result='error', error_msg='This user_name already exists', total_updated=0)
        total_updated = 0
        # update password if specified
        if data.password:
            if not password_helper.verify_and_update(data.password, user.hashed_password):
                return TableUpdateRowResult(result='error', error_msg='Invalid password', total_updated=0)
            user.hashed_password = password_helper.hash(data.password)
            total_updated += 1

        for col in su_manage_users_edit_columns:
            if col == 'password':
                continue
            # forbid editing certain columns for the same user
            if (user.user_id == cur_user_id) and (col in ('user_name', 'email', 'is_active', 'is_superuser')):
                continue
            value = getattr(data, col, None)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(user, col, value)
                total_updated = 1
        
        await self.session.commit()
        return TableUpdateRowResult(result='success', total_updated=total_updated)

    
    async def mark_deleted_by_user_id(self, cur_user_id: int, user_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by user_id.
        """
        # forbid delete himself
        if user_id == cur_user_id:
            return TableDeleteRowResult(result='error', error_msg='User cannot delete himself', total_deleted=0)
        try:
            result = await self.session.execute(select(User).where(User.user_id == user_id))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            row.email = f'deleted_{user_id}__' + row.email
            row.user_name = f'deleted_{user_id}__' + row.user_name
            await self.session.commit()
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in SuManageUsersTable.mark_deleted_by_user_id ({cur_user_id=}, {user_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
