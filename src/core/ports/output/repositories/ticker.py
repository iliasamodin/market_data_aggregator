from abc import ABC, abstractmethod

from src.core.domain.entities.ticker import TickerEntity


class TickerRepositoryPort(ABC):
    """
    Port for retrieving tickers and their calculation configurations.
    """

    @abstractmethod
    def get_all_active(self) -> list[TickerEntity]: ...
