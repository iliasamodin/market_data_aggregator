from collections import defaultdict
from collections.abc import Collection

from tradingview_ta import get_multiple_analysis

from src.core.application.exceptions.providers import FailedToGetMarketDataException
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.constants.screener import ScreenerEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.domain.value_objects.operational_data.indicators import IndicatorsSnapshotVO
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from src.core.ports.output.providers.market_data import MarketDataProviderPort


class TradingViewMarketDataProvider(MarketDataProviderPort):
    """
    TradingView implementation of MarketDataProviderPort.

    Fetches technical analysis snapshots for each ticker
    using the tradingview-ta library.
    """

    @exc_translator(
        reraise=FailedToGetMarketDataException,
        skip=FailedToGetMarketDataException,
    )
    def get_bulk_snapshots(
        self,
        tickers: Collection[TickerEntity],
        timeframe: TimeframeEnum,
    ) -> dict[CustomUUID, MarketDataSnapshotVO]:
        """
        Returns a market data snapshot for each ticker.

        The port contract does not restrict callers
        to passing tickers of a single screener,
        but get_multiple_analysis rejects mixed-screener calls.
        Grouping by screener here is therefore defensive:
        it enforces the API constraint regardless
        of how callers partition the input.
        Callers that already split by screener
        (e.g. to parallelise requests across screeners)
        will produce single-element groups — that is expected,
        not a duplication of logic.

        :param tickers: Tickers to fetch snapshots for.
        :param timeframe: Timeframe to fetch data at.

        :return: Map of ticker IDs to market data snapshots.
        """

        map_of_screeners_and_tickers: dict[ScreenerEnum, list[TickerEntity]] = defaultdict(list)
        for ticker in tickers:
            map_of_screeners_and_tickers[ticker.screener].append(ticker)

        map_of_ticker_ids_and_snapshots: dict[CustomUUID, MarketDataSnapshotVO] = {}
        for screener, screener_tickers in map_of_screeners_and_tickers.items():
            symbol_to_ticker = {f"{ticker.exchange.key}:{ticker.key}": ticker for ticker in screener_tickers}

            analysis_map = get_multiple_analysis(
                screener=screener.value,
                interval=timeframe.value,
                symbols=list(symbol_to_ticker),
            )

            for symbol_key, analysis in analysis_map.items():
                ticker = symbol_to_ticker[symbol_key]

                if not analysis:
                    raise FailedToGetMarketDataException(
                        params={
                            "ticker": ticker,
                            "timeframe": timeframe,
                            "analysis": analysis,
                        },
                    )

                indicators = IndicatorsSnapshotVO.model_validate(analysis.indicators)
                snapshot = MarketDataSnapshotVO(
                    ticker_id=ticker.id,
                    timeframe=timeframe,
                    open=analysis.indicators.get("open"),
                    high=analysis.indicators.get("high"),
                    low=analysis.indicators.get("low"),
                    close=analysis.indicators.get("close"),
                    volume=analysis.indicators.get("volume"),
                    indicators=indicators,
                )

                map_of_ticker_ids_and_snapshots[ticker.id] = snapshot

        return map_of_ticker_ids_and_snapshots
