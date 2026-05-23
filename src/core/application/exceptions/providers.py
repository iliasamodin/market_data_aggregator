from abc import ABC

from src.core.application.exceptions.shared import BaseApplicationException


class BaseProviderException(BaseApplicationException, ABC):
    """
    Base translated provider exception.
    """


class FailedToGetMarketDataException(BaseProviderException):
    """
    Failed to retrieve market data from external provider.
    """

    _DETAIL = "Failed to retrieve market data from external provider."


class FailedToSendNotificationException(BaseProviderException):
    """
    Failed to send notification to external system.
    """

    _DETAIL = "Failed to send notification to external system."
