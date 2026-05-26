from src.adapters.primary.http.configs import http_server_configs
from src.bootstrap.web import app


if __name__ == "__main__":
    app.start(
        host=http_server_configs.HOST,
        port=http_server_configs.PORT,
    )
