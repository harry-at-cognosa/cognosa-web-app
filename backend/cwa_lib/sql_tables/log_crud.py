import json
from fastapi import Request
from common.helpers import shorten
from common.sql_db_async import AsyncSession
from common.sql_models.api_users import User
from common.sql_models.log_crud import LogCRUD
from cwa_lib.app import get_client_ip


class LogCRUDTable:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.last_row: LogCRUD | None = None

    async def add_one(
            self, 
            user: User,
            request: Request,
            data: dict | None = None
            ):
        log_crud = LogCRUD(
            group_id=user.group_id,
            user_id=user.user_id,
            user_name=user.user_name,
            source_addr=shorten(get_client_ip(request), 65000),
            method=request.method,
            dest_addr=shorten(str(request.url), 65000),
            data=shorten(json.dumps(data, indent=1), 65000) if data else '',
        )
        self.session.add(log_crud)
        await self.session.commit()
        self.last_row = log_crud

    async def write_result(self, result):
        if not self.last_row:
            return
        self.last_row.result = shorten(repr(result), 65000)
        await self.session.commit()
