from pydantic import BaseModel, ConfigDict


class BaseVO(BaseModel):
    """
    Base class for Value Objects.
    """

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
    )


class BaseVOWithTitle(BaseVO):
    """
    Base class for Value Objects with title.
    """

    title: str
