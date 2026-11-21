from fastapi import Depends, HTTPException, status
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User, ApiGroups
from cwa_lib.users import current_active_user


async def chat_user(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(async_get_session),
) -> User:
    """A logged-in user whose group has chat switched on.

    Checked on every request: hiding the nav entry in the browser is not the
    barrier, this is. Applies to superusers too; chat is a group attribute.
    """
    group = await session.get(ApiGroups, user.group_id)
    if not group or group.deleted or not group.chat_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat is not enabled for this group")
    return user
