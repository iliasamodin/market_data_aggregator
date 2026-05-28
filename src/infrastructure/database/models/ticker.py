import uuid

from sqlalchemy import UUID, Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.constants.screener import ScreenerEnum
from src.infrastructure.database.configs import db_configs
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.exchange import ExchangeModel


class TickerModel(Base):
    """
    ORM model for the tickers table.

    Represents a tradable instrument.
    """

    __tablename__ = "tickers"
    __table_args__ = (
        UniqueConstraint(
            "key",
            "exchange_id",
        ),
        {
            "schema": db_configs.DB_SCHEMA,
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )
    screener: Mapped[ScreenerEnum] = mapped_column(
        Enum(ScreenerEnum),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    exchange_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            ExchangeModel.id,
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
