from time import sleep
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from common import DATABASE_SYNC_URL, log

sql_sync_engine = create_engine(
    url=DATABASE_SYNC_URL, 
    echo=False, 
    pool_pre_ping=True, 
    pool_size=5, 
    max_overflow=10
)

def get_sessionmaker(engine: Engine):
    return sessionmaker(bind=engine, expire_on_commit=False)

def get_engine_sessionmaker()-> tuple[Engine, sessionmaker[Session]]:
    sql_sync_engine = create_engine(
        url=DATABASE_SYNC_URL, 
        echo=False, 
        pool_pre_ping=True, 
        pool_size=5, 
        max_overflow=10
    )
    return sql_sync_engine, sessionmaker(bind=sql_sync_engine, expire_on_commit=False)


def wait_for_database(
    max_retries: int = 3600,
    retry_delay: float = 1.0
):
    """
    Wait for PostgreSQL database to become available.
    """
    engine, sessionmaker = get_engine_sessionmaker()
    for attempt in range(max_retries):
        try:
            with sessionmaker() as session:
                bool(session.execute(text("SELECT 1")).scalar_one_or_none())
            engine.dispose()
            return
        except OperationalError as e:
            if attempt % 60 == 0:
                log.info('wait_for_database: retrying...')
            if attempt < max_retries - 1:
                sleep(retry_delay)
                continue
            else:
                log.error('wait_for_database: Too many retries.')
                engine.dispose()
                exit(-1)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            engine.dispose()
            exit(-1)
