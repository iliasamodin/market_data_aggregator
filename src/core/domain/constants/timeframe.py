from enum import StrEnum


class TimeframeEnum(StrEnum):
    """
    Ticker bar timeframe.
    """

    INTERVAL_1_HOUR = "1h"
    INTERVAL_4_HOURS = "4h"
    INTERVAL_1_DAY = "1d"
    INTERVAL_1_WEEK = "1W"
    INTERVAL_1_MONTH = "1M"
