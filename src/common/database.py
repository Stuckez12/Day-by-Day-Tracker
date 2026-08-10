from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
