from abc import ABC, abstractmethod
from collections.abc import Collection

from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from src.core.domain.utils.custom_uuid import CustomUUID


class MarketDataProviderPort(ABC):
    """
    Port for retrieving market data of tickers.
    """

    @abstractmethod
    def get_bulk_snapshots(
        self,
        tickers: Collection[TickerEntity],
        timeframe: TimeframeEnum,
    ) -> dict[CustomUUID, MarketDataSnapshotVO]: ...
