from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class HTTPServerConfigs(BaseSettings):
    # API
    HOST: str = "0.0.0.0"
    PORT: int = 1500
    API_PREFIX: str = "/api"

    # Auth
    API_AUTH_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )


http_server_configs = HTTPServerConfigs()  # type: ignore
