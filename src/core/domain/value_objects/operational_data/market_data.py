from pydantic import BaseModel

from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.value_objects.operational_data.indicators import IndicatorsSnapshotVO
from src.core.domain.utils.custom_uuid import CustomUUID


class MarketDataSnapshotVO(BaseModel):
    """
    Current values for ticker operational data
    by configuration timeframe.
    """

    ticker_id: CustomUUID
    timeframe: TimeframeEnum

    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None

    indicators: IndicatorsSnapshotVO
