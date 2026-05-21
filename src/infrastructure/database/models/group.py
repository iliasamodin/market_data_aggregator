import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.algorithm_config import AlgorithmConfigModel
from src.infrastructure.database.configs import db_configs
from src.infrastructure.database.models.base import Base


class GroupModel(Base):
    """
    ORM model for the groups table.

    Represents an AND-conjunction of algorithm configs.
    A trading signal fires only
    when every linked algorithm config evaluates to true
    for a given ticker snapshot.
    """

    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


class GroupAlgorithmConfigModel(Base):
    """
    ORM model for the group_algorithm_configs table.

    Associates groups with algorithm configs
    in a many-to-many relationship.
    """

    __tablename__ = "group_algorithm_configs"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "algorithm_config_id",
        ),
        {
            "schema": db_configs.DB_SCHEMA,
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            GroupModel.id,
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    algorithm_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            AlgorithmConfigModel.id,
            ondelete="CASCADE",
        ),
        nullable=False,
    )
