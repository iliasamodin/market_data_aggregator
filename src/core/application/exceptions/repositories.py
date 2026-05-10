from abc import ABC

from src.core.application.exceptions.shared import BaseApplicationException


class BaseRepositoryException(BaseApplicationException, ABC):
    """
    Base translated repository exception.
    """


class FailedToGetTickersException(BaseRepositoryException):
    """
    Failed to retrieve tickers from the repository.
    """

    _DETAIL = "Failed to retrieve tickers from the repository."


class FailedToGetGroupsException(BaseRepositoryException):
    """
    Failed to retrieve groups from the repository.
    """

    _DETAIL = "Failed to retrieve groups from the repository."


class FailedToGetAlgorithmConfigsException(BaseRepositoryException):
    """
    Failed to retrieve algorithm configs from the repository.
    """

    _DETAIL = "Failed to retrieve algorithm configs from the repository."


class FailedToCheckRecentSignalException(BaseRepositoryException):
    """
    Failed to check for a recent signal in the repository.
    """

    _DETAIL = "Failed to check for a recent signal in the repository."


class FailedToSaveSignalException(BaseRepositoryException):
    """
    Failed to save a signal to the repository.
    """

    _DETAIL = "Failed to save a signal to the repository."
