from adapters.primary.http.robyn_app.application import app
from adapters.primary.http.configs import http_adapter_configs


if __name__ == "__main__":
    app.start(
        host=http_adapter_configs.HOST,
        port=http_adapter_configs.PORT,
    )
