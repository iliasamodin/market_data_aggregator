import uuid

from sqlalchemy import UUID, Boolean, Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.moving_average import MovingAverageEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.infrastructure.database.models.base import Base


class AlgorithmConfigModel(Base):
    """
    ORM model for the algorithm_configs table.

    Maps each algorithm configuration
    to the AlgorithmConfigEntity domain entity.
    Stores the algorithm type, its operating timeframe,
    evaluation threshold (level), and optional moving-average type.
    """

    __tablename__ = "algorithm_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    algorithm: Mapped[AlgorithmEnum] = mapped_column(
        Enum(AlgorithmEnum),
        nullable=False,
    )
    timeframe: Mapped[TimeframeEnum] = mapped_column(
        Enum(TimeframeEnum),
        nullable=False,
    )
    level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    moving_average: Mapped[MovingAverageEnum | None] = mapped_column(
        Enum(MovingAverageEnum),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
