from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseConfigs(BaseSettings):
    # Connection parameters
    DB_HOST: str = Field(default="0.0.0.0")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SCHEMA: str = Field(default="trading")

    # Database pooling
    DB_POOL_SIZE: int = Field(
        default=10,
        ge=1,
    )
    DB_MAX_OVERFLOW: int = Field(
        default=20,
        ge=0,
    )

    # Alembic
    DB_ALEMBIC_SCHEMA: str = Field(default="alembic")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )

    @property
    def dsn(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


db_configs = DatabaseConfigs()  # type: ignore
