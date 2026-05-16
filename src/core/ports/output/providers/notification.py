from abc import ABC, abstractmethod

from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.ticker import TickerEntity


class NotificationProviderPort(ABC):
    """
    Port for sending notifications to external systems.
    """

    @abstractmethod
    def send_signal_alert(
        self,
        ticker: TickerEntity,
        group: GroupEntity,
    ) -> SignalStatusEnum: ...
