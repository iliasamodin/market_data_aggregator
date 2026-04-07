from enum import StrEnum


class SignalStatusEnum(StrEnum):
    """
    Status of a trading signal.
    """

    CREATED = "created"
    SENT = "sent"
    FAILED = "failed"
