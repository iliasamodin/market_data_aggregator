from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class HTTPAdapterConfigs(BaseSettings):
    # API
    HOST: str = "0.0.0.0"
    PORT: int = 1500
    API_PREFIX: str = "/api"

    model_config = SettingsConfigDict(env_file=".env")


http_adapter_configs = HTTPAdapterConfigs()
