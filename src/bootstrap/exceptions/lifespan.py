from abc import ABC

from src.core.application.exceptions.shared import BaseApplicationException


class BaseLifespanException(BaseApplicationException, ABC):
    """
    Base exception for lifespan.
    """


class FailedToCloseEngineConnectsToDBException(BaseLifespanException):
    """
    Failed to close engine connections to DB.
    """

    _DETAIL = "Failed to close engine connections to DB."
