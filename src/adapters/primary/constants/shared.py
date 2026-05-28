from enum import StrEnum

DETAIL = "detail"


class UnsuccessfulResponseDetailEnum(StrEnum):
    """
    Detailed error messages for unsuccessful responses.
    """

    INTERNAL_SERVER_ERROR = "Internal server error."
    MISSING_OR_INVALID_AUTH_HEADER = "Missing or invalid authorization header."
