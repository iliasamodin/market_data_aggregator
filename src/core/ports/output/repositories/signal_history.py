from abc import ABC, abstractmethod
from datetime import timedelta

from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.signal_history import HistoricalSignalEntity
from src.core.domain.utils.custom_uuid import CustomUUID


class SignalHistoryRepositoryPort(ABC):
    """
    Port for working with history of signal.
    """

    @abstractmethod
    def has_recent_signal(
        self,
        calculation_config_id: CustomUUID,
        delta: timedelta,
        status: SignalStatusEnum,
    ) -> bool: ...

    @abstractmethod
    def save(self, signal: HistoricalSignalEntity) -> None: ...
