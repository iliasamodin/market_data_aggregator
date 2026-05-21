from sqlalchemy import create_engine

from src.infrastructure.database.configs import db_configs

engine = create_engine(
    db_configs.dsn,
    pool_size=db_configs.DB_POOL_SIZE,
    max_overflow=db_configs.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)
