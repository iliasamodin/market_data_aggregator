import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class ExchangeModel(Base):
    """
    ORM model for the exchanges table.

    Represents a trading exchange.
    """

    __tablename__ = "exchanges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
