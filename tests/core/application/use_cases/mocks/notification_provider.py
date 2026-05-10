from src.core.application.exceptions.providers import FailedToSendNotificationException
from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.ports.output.providers.notification import NotificationProviderPort


class InMemoryNotificationProvider(NotificationProviderPort):
    """
    In memory provider for sending trading signal alert notifications.
    Tracks all dispatched alerts
    and supports a configurable failure mode.
    """

    def __init__(self, should_fail: bool = False):
        self._should_fail = should_fail
        self.sent_alerts: list[tuple[TickerEntity, GroupEntity]] = []

    def send_signal_alert(
        self,
        ticker: TickerEntity,
        group: GroupEntity,
    ) -> SignalStatusEnum:
        if self._should_fail:
            raise FailedToSendNotificationException()

        self.sent_alerts.append((ticker, group))
        signal_status = SignalStatusEnum.SENT

        return signal_status
