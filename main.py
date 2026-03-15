from adapters.primary.http.robyn_app.application import app
from src.configs import settings


if __name__ == "__main__":
    app.start(
        host=settings.HOST,
        port=settings.PORT,
    )
