from datetime import UTC, datetime, timedelta

from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.signal_history import HistoricalSignalEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.signal_history import SignalHistoryRepositoryPort


class InMemorySignalHistoryRepository(SignalHistoryRepositoryPort):
    """
    In memory repository for storing and querying the history
    of trading signals.
    """

    def __init__(self, signals: list[HistoricalSignalEntity] | None = None):
        self._signals: list[HistoricalSignalEntity] = signals or []

    def has_recent_signal(
        self,
        calculation_config_id: CustomUUID,
        delta: timedelta,
        status: SignalStatusEnum,
    ) -> bool:
        cutoff = datetime.now(tz=UTC) - delta
        has_signal_within_expiration = any(
            signal.calculation_config_id == calculation_config_id
            and signal.status == status
            and signal.create_dt >= cutoff
            for signal in self._signals
        )

        return has_signal_within_expiration

    def save(self, signal: HistoricalSignalEntity) -> None:
        for idx, existing in enumerate(self._signals):
            if existing.id == signal.id:
                self._signals[idx] = signal
                return

        self._signals.append(signal)

    @property
    def signals(self) -> list[HistoricalSignalEntity]:
        return self._signals
