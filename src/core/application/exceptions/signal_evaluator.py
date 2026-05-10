from abc import ABC

from src.core.application.exceptions.shared import BaseApplicationException, BaseEntitiesMissingException


class BaseSignalEvaluatorException(BaseApplicationException, ABC):
    """
    Base exception for signal evaluation.
    """


class TickersMissingException(
    BaseSignalEvaluatorException,
    BaseEntitiesMissingException,
):
    """
    No tickers available for trading signal evaluation.
    """

    _DETAIL = "No tickers available for trading signal evaluation."


class GroupsMissingException(
    BaseSignalEvaluatorException,
    BaseEntitiesMissingException,
):
    """
    No groups available for trading signal evaluation.
    """

    _DETAIL = "No groups available for trading signal evaluation."


class AlgorithmConfigsMissingException(
    BaseSignalEvaluatorException,
    BaseEntitiesMissingException,
):
    """
    No algorithm configurations available for trading signal evaluation.
    """

    _DETAIL = "No algorithm configurations available for trading signal evaluation."
