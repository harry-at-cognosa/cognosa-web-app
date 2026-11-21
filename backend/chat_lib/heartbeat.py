import asyncio
from traceback import format_exc
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from common import log
from common.sql_db_async import SqlAsyncSession
from common.sql_models import ApiProcesses
from common.watchdogs import AP_SLEEP_TIME

# Deliberately not 'run_tasks': the web app's stale-task sweep treats a live
# 'run_tasks' watchdog row as proof that a query runner is up.
AP_TYPE = 'chat_service'
AP_NAME = 'chat_service'
AP_SUBNAME = 'service'


class Heartbeat:
    """Keeps this service's row in `api_processes` fresh (Server Status page)."""
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None

    @staticmethod
    async def _write(ap_status: str) -> None:
        stmt = insert(ApiProcesses).values(
            ap_type=AP_TYPE, ap_name=AP_NAME, ap_subname=AP_SUBNAME,
            ap_status=ap_status, ap_updated_at=func.now(),
        ).on_conflict_do_update(
            index_elements=['ap_name', 'ap_subname'],
            set_={'ap_type': AP_TYPE, 'ap_status': ap_status, 'ap_updated_at': func.now()},
        )
        async with SqlAsyncSession() as session:
            await session.execute(stmt)
            await session.commit()

    async def _loop(self) -> None:
        while True:
            try:
                await self._write('running')
            except asyncio.CancelledError:
                raise
            except Exception:
                log.error(f"Chat heartbeat failed:\n{format_exc()}")
            await asyncio.sleep(AP_SLEEP_TIME)

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop(), name='chat_heartbeat')

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        try:
            await self._write('exit')
        except Exception:
            log.error(f"Chat heartbeat exit write failed:\n{format_exc()}")
