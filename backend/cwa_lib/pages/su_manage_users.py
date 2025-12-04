from sqlalchemy import select
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from common.sql_tools import fix_autoincrement
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.su_manage_users import SuManageUsersRead, SuManageUsersCreate, SuManageUsersUpdate
from cwa_lib.pages import GenericTableRead

from cwa_lib.sql_tables.api_users import ApiUsersTable
from cwa_lib.users import password_helper
from cwa_lib.validators.user_name import check_unique__email, check_unique__user_name


su_manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', type='number'),
    'group_id': ColumnType(display='Group ID: Name', type='group_id_name', default=1, select=[]),
    'user_name': ColumnType(
        display='User name', type='string', cu_required=True, 
        cu_edit_msg="user_name must contain only lowercase letters, numbers, underscores, or hyphens"
    ),
    'full_name': ColumnType(
        display='Full name', type='string', cu_required=True, 
        cu_edit_msg="Full name must be from 3 to 32 characters"
    ),
    'email': ColumnType(
        display='Email', type='string', cu_required=True, 
        cu_edit_msg="Enter valid email"
    ),
    'password': ColumnType(
        display='New Password', type='groupadmin_user_password',
        cu_edit_msg="Password must be at least 8 characters"
    ),
    'is_active': ColumnType(
        display='Active', type='boolean', default=True,
        cu_edit_msg="User is enabled?"
    ),
    'is_contentmanager': ColumnType(
        display='Content\nManager', type='boolean', default=False,
        cu_edit_msg="User is Content Manager?"
    ),
    'is_groupadmin': ColumnType(
        display='Group\nAdmin', type='boolean', default=False,
        cu_edit_msg="User is Group Admin?"
    ),
    'is_superuser': ColumnType(
        display='Super\nUser', type='boolean', default=False,
        cu_edit_msg="User is Super User?"
    ),
    'last_seen': ColumnType(display='Last seen', type='datetime'),
    'created_at': ColumnType(display='Created at', type='datetime'),
}
su_manage_users__all_columns = list(su_manage_users__query_columns.keys())
su_manage_users_edit_columns = [x for x in su_manage_users__all_columns if (x not in ('user_id', 'created_at'))]

su_manage_users__table_options = TableOptions(
    title='SU Manage Users',
    pk='user_id',
    read__visible_columns=[x for x in su_manage_users__all_columns if (x != 'password')],
    read__hide_on_false=['is_contentmanager', 'is_groupadmin', 'is_superuser'],  # table view: hide if false
    create__ask_columns=su_manage_users_edit_columns,
    update__ask_columns=su_manage_users_edit_columns,
    delete__ask_columns=['user_name', 'full_name', 'email'],
    order_by__allow=su_manage_users__all_columns,
)

class SuManageUsersTableRead(GenericTableRead):
    sa_model = User
    read_model = SuManageUsersRead
    name = 'su_manage_users'
    query_columns = su_manage_users__query_columns
    table_options = su_manage_users__table_options
    default_order_by = table_options.pk
    qc_to_user_group = {'group_id': ('add_values', 'select_default', 'allow_all')}

    def _get_where_clause(self):
        where_clause = User.user_id > -1
        if (deleted := self.kwargs.get('deleted', 0)) is not None:
            where_clause &= User.deleted == deleted
        return where_clause

class SuManageUsersTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_one(self, data: SuManageUsersCreate) -> TableCreateRowResult:
        """
        Create one row
        """
        await fix_autoincrement(self.session, User)
        # check if user exists with the same email or user_name
        await check_unique__email(self.session, data.email)
        await check_unique__user_name(self.session, data.user_name)
        
        await ApiUsersTable.create_user(
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
        where_clause = (User.user_id == data.user_id) & (User.deleted == 0)
        result = await self.session.execute(select(User).where(where_clause))
        user = result.scalar_one_or_none()
        if not user:
            return TableUpdateRowResult(result='error', total_updated=0)
        # check if user exists with the same email or user_name
        if data.email and (data.email != user.email):
            await check_unique__email(self.session, data.email)
        if data.user_name and (data.user_name != user.user_name):
            await check_unique__user_name(self.session, data.user_name)
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
            where_clause = (User.user_id == user_id) & (User.deleted == 0)
            result = await self.session.execute(select(User).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            row.email = (f'deleted_{user_id}__' + row.email)[:320]
            row.user_name = (f'deleted_{user_id}__' + row.user_name)[:32]
            await self.session.commit()
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in SuManageUsersTable.mark_deleted_by_user_id ({cur_user_id=}, {user_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
