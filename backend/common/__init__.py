import os
import sys
from dotenv import load_dotenv
from common.helpers import split2list

SCRIPT_NAME = os.path.basename(sys.argv[0])
WORK_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR_STATIC = os.path.join(WORK_DIR, 'static')
FRONTEND_DIR_TEMPLATES = os.path.join(WORK_DIR, 'templates')

API_URL_PREFIX = '/api/v1'

load_dotenv(dotenv_path=os.path.join(WORK_DIR, '.env'), verbose=True)

CORS_ORIGINS = split2list(os.getenv("CORS_ORIGINS", "http://localhost:5173"), ',', str)
DATABASE_URL = os.getenv("DATABASE_URL", "DATABASE_URL_NOT_SPECIFIED_IN_ENV")
DATABASE_ASYNC_URL = DATABASE_URL.replace('database://', 'postgresql+asyncpg://')  # for asynchronous PostgreSQL library
DATABASE_SYNC_URL = DATABASE_URL.replace('database://', 'postgresql+psycopg2://')  # for synchronous PostgreSQL library

LOG_SQLALCHEMY_RT = os.getenv("LOG_SQLALCHEMY_RT", 'NOTSET')
RT_VDB_PROCESS_NUM = int(os.getenv("RT_VDB_PROCESS_NUM", 1))
RT_VDB_EMB_MODELS_PRELOAD = split2list(os.getenv("RT_VDB_EMB_MODELS_PRELOAD", ''), ',', str)

from .async_log import AsyncLogger
log = AsyncLogger()
