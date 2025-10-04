from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from common.sql_models.api_users import User
from common import DATABASE_ASYNC_URL
from common.sql_models import Base

sql_async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=False, future=True)
SqlAsyncSession = async_sessionmaker(sql_async_engine, expire_on_commit=False, class_=AsyncSession)

async def async_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SqlAsyncSession() as session:
        yield session

async def async_create_db_and_tables():
    async with sql_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_get_user_db(session: AsyncSession = Depends(async_get_session)):
    yield SQLAlchemyUserDatabase(session, User)

