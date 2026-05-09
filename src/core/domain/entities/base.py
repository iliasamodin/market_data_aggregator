from pydantic import BaseModel, Field, ConfigDict
from uuid_utils import uuid7

from src.core.domain.utils.custom_uuid import CustomUUID


class BaseEntity(BaseModel):
    """
    Base class for entities.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )


class BaseEntityWithID(BaseEntity):
    """
    Base class for entities with ID.
    """

    id: CustomUUID = Field(default_factory=uuid7)


class BaseEntityWithIDAndTitle(BaseEntityWithID):
    """
    Base class for entities with ID and title.
    """

    title: str
