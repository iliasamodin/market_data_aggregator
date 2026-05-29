from sqlalchemy.orm import DeclarativeBase

from src.infrastructure.database.configs import db_configs


class Base(DeclarativeBase):
    __table_args__ = {
        "schema": db_configs.DB_SCHEMA,
    }
