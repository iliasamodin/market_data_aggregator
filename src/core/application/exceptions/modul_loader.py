from abc import ABC

from src.core.application.exceptions.shared import BaseApplicationException


class BaseModuleLoaderException(BaseApplicationException, ABC):
    """
    Base exception for module loader.
    """


class BaseDirectoryNotFoundException(BaseModuleLoaderException):
    """
    The 'src' base directory was not found in the file path hierarchy.
    """

    _DETAIL = "The 'src' base directory was not found in the file path hierarchy."


class FailedToLoadModuleException(BaseModuleLoaderException):
    """
    Failed to dynamically import the target module via importlib.
    """

    _DETAIL = "Failed to dynamically import the target module via importlib."
