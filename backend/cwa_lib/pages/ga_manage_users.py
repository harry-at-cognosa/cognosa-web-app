from sqlalchemy import select
from common import log
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User
from common.sql_tools import create_order_clause, fix_autoincrement
from cwa_lib.pydantic_schemas.generic_table import (
    ColumnType, TableOptions, TableQuery, TableCreateRowResult, TableUpdateRowResult, TableDeleteRowResult
)
from cwa_lib.pydantic_schemas.ga_manage_users import GaManageUsersQueryResult, GaManageUsersCreate, GaManageUsersUpdate
from cwa_lib.sql_tables.api_users import ApiUsersTable
from cwa_lib.app import password_helper


ga_manage_users__query_columns = {
    'user_id': ColumnType(display='UserID', type='number'),
    'user_name': ColumnType(display='User name', type='string'),
    'full_name': ColumnType(display='Full name', type='string'),
    'email': ColumnType(display='Email', type='string'),
    'password': ColumnType(display='New Password', type='groupadmin_user_password'),
    'is_active': ColumnType(display='Active', type='boolean', default=True),
    'is_contentmanager': ColumnType(display='Content\nManager', type='boolean', default=False),
    'is_groupadmin': ColumnType(display='Group\nAdmin', type='boolean', default=False),
    'created_at': ColumnType(display='Created at', type='datetime'),
}
ga_manage_users__all_columns = list(ga_manage_users__query_columns.keys())
ga_manage_users_edit_columns = [x for x in ga_manage_users__all_columns if (x not in ('user_id', 'created_at'))]

ga_manage_users__table_options = TableOptions(
    title='Manage Users',
    pk='user_id',
    read__visible_columns=[x for x in ga_manage_users__all_columns if (x != 'password')],
    read__hide_on_false=['is_contentmanager', 'is_groupadmin'],  # table view: hide if false
    create__ask_columns=ga_manage_users_edit_columns,
    update__ask_columns=ga_manage_users_edit_columns,
    delete__ask_columns=['user_name', 'full_name', 'email'],
    order_by__allow=ga_manage_users__all_columns,
)


class GaManageUsersTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_all(
            self,
            cur_user_id: int,
            cur_group_id: int,
            payload: TableQuery
            ) -> GaManageUsersQueryResult:
        order_clause, order_by, order_dir = create_order_clause(
            model=User, 
            default_order_by=ga_manage_users__table_options.pk, 
            order_by=payload.order_by, 
            order_dir=payload.order_dir
        )
        # ignore deleted users, users from other groups, superusers (if it is not the same user)
        where_clause = (User.deleted == 0) & (User.group_id == cur_group_id)
        where_clause &= ((User.user_id == cur_user_id) | (User.is_superuser == False))
        result = await self.session.execute(
            select(User)
            .where(where_clause)
            .order_by(order_clause)
            .limit(payload.limit)
            .offset(payload.offset)
        )
        rows = result.scalars().all()
        for row in rows:
            row.password = ''
        return GaManageUsersQueryResult(
            name='ga_manage_users',
            rows=rows,
            columns=ga_manage_users__query_columns,
            table_options=ga_manage_users__table_options,
            order_by=order_by,
            order_dir=order_dir,
            total=len(rows)
        )
    
    async def create_one(self, cur_group_id: int, data: GaManageUsersCreate) -> TableCreateRowResult:
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
            group_id=cur_group_id,
            is_active=data.is_active,
            is_verified=True,
            is_groupadmin=data.is_groupadmin,
            is_contentmanager=data.is_contentmanager
        )
        return TableCreateRowResult(result='success', total_created=1)
    
    async def update_one(self, cur_user_id: int, cur_group_id: int, data: GaManageUsersUpdate) -> TableUpdateRowResult:
        """
        Update one row
        """
        # Forbid editing superusers (if it is not the same user) or users from other groups
        where_clause = (User.user_id == data.user_id) & (User.group_id == cur_group_id)
        where_clause &= ((User.user_id == cur_user_id) | (User.is_superuser == False))
        result = await self.session.execute(select(User).where(where_clause))
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

        for col in ga_manage_users_edit_columns:
            if col == 'password':
                continue
            # forbid editing certain columns for the same user
            if (user.user_id == cur_user_id) and (col in ('user_name', 'email', 'is_active', 'is_groupadmin')):
                continue
            value = getattr(data, col, None)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(user, col, value)
                total_updated = 1
        
        await self.session.commit()
        return TableUpdateRowResult(result='success', total_updated=total_updated)

    
    async def mark_deleted_by_user_id(self, cur_user_id: int, cur_group_id: int, user_id: int) -> TableDeleteRowResult:
        """
        Mark deleted one row by user_id.
        """
        if user_id == cur_user_id:
            return TableDeleteRowResult(result='error', error_msg='User cannot delete himself', total_deleted=0)
        # forbid delete superusers or users from other groups
        where_clause = (User.user_id == user_id) & (User.group_id == cur_group_id) & (User.is_superuser == False)
        try:
            result = await self.session.execute(select(User).where(where_clause))
            if not (row := result.scalar_one_or_none()):            
                return TableDeleteRowResult(result='error', total_deleted=0)
            row.deleted = 1
            row.email = f'deleted_{user_id}__' + row.email
            row.user_name = f'deleted_{user_id}__' + row.user_name
            await self.session.commit()
            return TableDeleteRowResult(result='success', total_deleted=1)
        except Exception as exc:
            log.error(f"Exception in GaManageUsersTable.mark_deleted_by_user_id ({cur_user_id=}, {cur_group_id=}, {user_id=}):\n{exc}")
            return TableDeleteRowResult(result='error', total_deleted=0)
