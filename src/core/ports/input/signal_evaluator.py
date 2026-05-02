from abc import ABC, abstractmethod

from src.core.application.dtos.signal_evaluator import SignalEvaluationResultDTO


class SignalEvaluatorInputPort(ABC):
    """
    Port of use case for market data collection
    and aggregation potential entry points.
    """

    @abstractmethod
    def execute(self) -> SignalEvaluationResultDTO: ...
