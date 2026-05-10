from collections.abc import Collection

from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from src.core.ports.output.providers.market_data import MarketDataProviderPort


class InMemoryMarketDataProvider(MarketDataProviderPort):
    """
    In memory provider for retrieving market data of tickers.
    """

    def __init__(
        self,
        map_of_snapshots: dict[CustomUUID, dict[TimeframeEnum, MarketDataSnapshotVO]] | None = None,
    ):
        self._map_of_snapshots = map_of_snapshots or {}

    def get_bulk_snapshots(
        self,
        tickers: Collection[TickerEntity],
        timeframe: TimeframeEnum,
    ) -> dict[CustomUUID, MarketDataSnapshotVO]:
        map_of_ticker_ids_and_snapshots: dict[CustomUUID, MarketDataSnapshotVO] = {}
        for ticker in tickers:
            map_of_timeframes_and_snapshots = self._map_of_snapshots.get(ticker.id, {})

            snapshot = map_of_timeframes_and_snapshots.get(timeframe)
            if snapshot is not None:
                map_of_ticker_ids_and_snapshots[ticker.id] = snapshot

        return map_of_ticker_ids_and_snapshots
