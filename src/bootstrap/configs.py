from dotenv import load_dotenv
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class LoggingConfigs(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("/app/logs")
    LOG_BACKUP_COUNT: int = Field(
        default=30,
        ge=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )


logging_configs = LoggingConfigs()
