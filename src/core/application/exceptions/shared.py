from abc import ABC

import logging
import sys
import traceback


class BaseApplicationException(Exception, ABC):
    """
    Base exception for application logic.
    """

    _DETAIL = "Application logic error."

    def __init__(self, **params):
        self._params = params
        self._traceback: str | None = None

        exc_type, _, _ = sys.exc_info()
        if exc_type is not None:
            self._traceback = traceback.format_exc()

        logging.log(
            level=logging.ERROR,
            msg=self.full_exc_info,
        )

    @property
    def detail(self) -> str:
        string_params = f"\nParameters: {self._params}" if self._params else ""
        detail = f"{self._DETAIL}{string_params}"

        return detail

    @property
    def full_exc_info(self) -> str:
        string_traceback = f"\nTraceback: {self._traceback}" if self._traceback else ""
        full_exc_info = f"{self.detail}{string_traceback}"

        return full_exc_info

    def __str__(self) -> str:
        return self.detail


class BaseEntitiesMissingException(BaseApplicationException, ABC):
    """
    Base exception for missing entities.
    """
