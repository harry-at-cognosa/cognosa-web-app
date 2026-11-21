"""Cognosa chat service (conversation mode).

A separate process from the web app and from run_tasks. Start with:

    uvicorn chat_service:app --port 8001

Run a single worker: the service keeps per-process state (embedding models,
the set of conversations with an answer in flight).
"""
from common import log
log.init('chat')
from common.sql_db_sync import wait_for_database
wait_for_database()

from chat_lib.app import app  # noqa: E402,F401
