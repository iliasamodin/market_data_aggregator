from typing import NamedTuple

from src.core.domain.constants.screener import ScreenerEnum
from src.core.domain.constants.timeframe import TimeframeEnum


class TimeframeAndScreenerKey(NamedTuple):
    """
    Key for timeframes and tickers map.
    """

    timeframe: TimeframeEnum
    screener: ScreenerEnum
