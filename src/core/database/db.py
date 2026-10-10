from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.settings import app_config


engine = create_engine(
    app_config.db_url,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


backup_engine = create_engine(
    app_config.backup_db_url,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

BackupSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=backup_engine)


def get_backup_db():
    db = BackupSessionLocal()

    try:
        yield db

    finally:
        db.close()


@contextmanager
def temporary_db_session(
    database_name: str,
) -> Generator[Session, None, None]:

    engine = create_engine(
        f"{app_config.base_db_url}/{database_name}",
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=3,
        pool_timeout=30,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
        engine.dispose()
