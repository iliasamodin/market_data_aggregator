from urllib.request import Request, urlopen

import certifi
import json
import ssl

from src.adapters.secondary.constants.http import HTTPMethodEnum
from src.core.application.exceptions.providers import FailedToSendNotificationException
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.ports.output.providers.notification import NotificationProviderPort
from src.infrastructure.telegram.configs import telegram_configs


class TelegramNotificationProvider(NotificationProviderPort):
    """
    Telegram implementation of NotificationProviderPort.

    Sends signal alerts to a configured Telegram chat
    via the Bot API using HTML parse mode.
    """

    @exc_translator(reraise=FailedToSendNotificationException)
    def send_signal_alert(
        self,
        ticker: TickerEntity,
        group: GroupEntity,
    ) -> SignalStatusEnum:
        """
        Sends a signal alert to the configured Telegram chat.

        Formats ticker and group information into a message
        and posts it via the Telegram Bot API.

        :param ticker: Ticker that triggered the signal.
        :param group: Group whose condition was met.

        :return: SENT status on successful delivery.
        """

        url = telegram_configs.TELEGRAM_SEND_MESSAGE_URL.format(token=telegram_configs.TELEGRAM_BOT_TOKEN)

        text = telegram_configs.TELEGRAM_SIGNAL_ALERT_TEMPLATE.format(
            ticker_title=ticker.title,
            exchange_key=ticker.exchange.key,
            group_title=group.title,
            group_description=group.description,
        )
        payload = json.dumps(
            {
                "chat_id": telegram_configs.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": telegram_configs.TELEGRAM_PARSE_MODE,
            }
        ).encode("utf-8")

        request = Request(
            url=url,
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method=HTTPMethodEnum.POST,
        )

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        with urlopen(
            request,
            timeout=telegram_configs.TELEGRAM_REQUEST_TIMEOUT,
            context=ssl_context,
        ):
            pass

        return SignalStatusEnum.SENT
