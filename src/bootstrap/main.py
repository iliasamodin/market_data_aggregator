from src.adapters.primary.http.configs import http_server_configs
from src.bootstrap.utils.configure_logs import configure_logging
from src.bootstrap.web import app

if __name__ == "__main__":
    configure_logging()

    app.start(
        host=http_server_configs.HOST,
        port=http_server_configs.PORT,
    )
