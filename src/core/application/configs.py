from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AppConfigs(BaseSettings):
    # Tools
    THREAD_POOL_MAX_WORKERS: int = Field(
        default=32,
        ge=8,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )


app_configs = AppConfigs()
