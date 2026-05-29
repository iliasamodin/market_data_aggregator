import logging.config

from src.bootstrap.configs import logging_configs


def configure_logging() -> None:
    """
    Configure application logging.

    Sets up two handlers:
        - console: writes to stdout for docker logs.
        - file: writes to <LOG_DIR>/<LOG_FILE_NAME>
        with daily rotation at midnight;
        keeps LOG_BACKUP_COUNT archived files compressed as .gz.
    """

    LOG_FILE_NAME = "app.log"

    logging_configs.LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "filename": logging_configs.LOG_DIR / LOG_FILE_NAME,
                    "when": "midnight",
                    "backupCount": logging_configs.LOG_BACKUP_COUNT,
                    "encoding": "utf-8",
                    "formatter": "default",
                },
            },
            "root": {
                "level": logging_configs.LOG_LEVEL,
                "handlers": ["console", "file"],
            },
        }
    )
