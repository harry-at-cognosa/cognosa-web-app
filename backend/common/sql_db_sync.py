from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from common import DATABASE_SYNC_URL

sql_sync_engine = create_engine(DATABASE_SYNC_URL, echo=False)
SqlSyncSession = sessionmaker(bind=sql_sync_engine, expire_on_commit=False)
