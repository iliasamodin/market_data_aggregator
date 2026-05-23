from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramConfigs(BaseSettings):
    # Connection parameters
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    TELEGRAM_SEND_MESSAGE_URL: str = Field(default="https://api.telegram.org/bot{token}/sendMessage")
    TELEGRAM_REQUEST_TIMEOUT: int = Field(
        default=10,
        ge=1,
    )

    # Notification parameters
    TELEGRAM_PARSE_MODE: str = Field(default="HTML")
    TELEGRAM_SIGNAL_ALERT_TEMPLATE: str = Field(
        default=(
            "<b>Trading Signal Alert</b>\n"
            "Ticker: <code>{ticker_title}</code> ({exchange_key})\n"
            "Group: <code>{group_title}</code>\n"
            "Description: {group_description}"
        ),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )


telegram_configs = TelegramConfigs()  # type: ignore
