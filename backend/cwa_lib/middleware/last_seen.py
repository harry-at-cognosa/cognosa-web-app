from datetime import datetime, timezone, timedelta
from traceback import format_exc
from sqlalchemy import update
from fastapi import Depends
from common import log
from common.sql_db_async import AsyncSession, async_get_session
from cwa_lib.users import User, current_active_user_or_none

LAST_SEEN_MIN_DELTA = timedelta(seconds=60)

async def refresh_last_seen(
    user: User = Depends(current_active_user_or_none),
    session: AsyncSession = Depends(async_get_session),
) -> None:
    """
    Global dependency: if there's an authenticated user, write last_seen.
    Skips update if last_seen is recent to reduce DB writes.
    """
    if not user:
        return

    try:
        # make timezone-aware UTC now
        now = datetime.now(timezone.utc)

        # If the user object already includes last_seen, check its recency to avoid writes.
        last_seen = getattr(user, "last_seen", None)
        if last_seen is not None:
            # convert naive to aware if needed (defensive)
            if last_seen.tzinfo is None:
                # assume stored in UTC if naive
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            if (now - last_seen) < LAST_SEEN_MIN_DELTA:
                return

        # Use SQL UPDATE to avoid needing to attach the object to session.
        await session.execute(
            update(User)
            .where(User.user_id == user.user_id)
            .values(last_seen=now)
        )
        await session.commit()
    except Exception:
        # rollback on failure and log; don't break the request
        try:
            await session.rollback()
        except Exception:
            pass
        log.error(f"Error updating last_seen for user {getattr(user,'id',None)}:\n{format_exc()}")
        return
