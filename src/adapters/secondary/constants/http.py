from enum import StrEnum


class HTTPMethodEnum(StrEnum):
    """
    Methods of HTTP requests.
    """

    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
