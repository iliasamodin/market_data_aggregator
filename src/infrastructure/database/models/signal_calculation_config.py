import uuid

from sqlalchemy import UUID, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.group import GroupModel
from src.infrastructure.database.models.ticker import TickerModel
from src.infrastructure.database.models.base import Base


class SignalCalculationConfigModel(Base):
    """
    ORM model for the signal_calculation_configs table.

    Links a ticker to a group and stores the expiration window
    used to deduplicate recently generated signals.
    """

    __tablename__ = "signal_calculation_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    ticker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            TickerModel.id,
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            GroupModel.id,
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    signal_expiration_timestamp: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
