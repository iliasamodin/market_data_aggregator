from collections import defaultdict
from concurrent.futures import Future, as_completed, wait
from datetime import timedelta
from typing import ClassVar

import threading
import logging

from src.core.application.configs import app_configs
from src.core.application.constants.signal_evaluator import SignalEvaluatorMessagesEnum
from src.core.application.dtos.map_keys import TimeframeAndScreenerKey
from src.core.application.dtos.maps import BidirectionalGroupAlgoConfigMapDTO, BidirectionalTickerGroupMapDTO
from src.core.application.dtos.signal_evaluator import SignalEvaluationResultDTO
from src.core.application.exceptions.signal_evaluator import (
    AlgorithmConfigsMissingException,
    GroupsMissingException,
    TickersMissingException,
)
from src.core.application.exceptions.providers import FailedToSendNotificationException
from src.core.application.utils.demonic_thread_pool import DemonicThreadPoolExecutor
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.entities.signal_calculation_config import SignalCalculationConfigEntity
from src.core.domain.entities.signal_history import HistoricalSignalEntity
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.input.signal_evaluator import SignalEvaluatorInputPort
from src.core.ports.output.repositories.ticker import TickerRepositoryPort
from src.core.ports.output.repositories.group import GroupRepositoryPort
from src.core.ports.output.repositories.algorithm_config import AlgorithmConfigRepositoryPort
from src.core.ports.output.repositories.signal_history import SignalHistoryRepositoryPort
from src.core.ports.output.providers.market_data import MarketDataProviderPort
from src.core.ports.output.providers.notification import NotificationProviderPort


class SignalEvaluatorUseCase(SignalEvaluatorInputPort):
    """
    Use case for market data collection
    and aggregation potential entry points.

    The class acts as an orchestrator:
    it coordinates the operation of repositories and external APIs
    to provide the domain strategies
    with the necessary data for evaluation.
    """

    # A single daemon thread attribute across all use case instances.
    # Since there is no point in concurrently invoking
    # multiple instances of the trading signal evaluation use case,
    # one instance will be sufficient
    # for all sequential execution iterations of the use case
    _thread_pool: ClassVar[DemonicThreadPoolExecutor] = DemonicThreadPoolExecutor(
        max_workers=app_configs.THREAD_POOL_MAX_WORKERS,
        daemon=True,
    )
    _lock: ClassVar[threading.RLock] = threading.RLock()

    def __init__(
        self,
        ticker_repo: TickerRepositoryPort,
        group_repo: GroupRepositoryPort,
        algorithm_repo: AlgorithmConfigRepositoryPort,
        signal_history_repo: SignalHistoryRepositoryPort,
        market_data_provider: MarketDataProviderPort,
        notification_provider: NotificationProviderPort,
    ):
        self._ticker_repo = ticker_repo
        self._group_repo = group_repo
        self._algo_repo = algorithm_repo
        self._history_repo = signal_history_repo

        self._market_data_provider = market_data_provider
        self._notification_provider = notification_provider

        self._result = SignalEvaluationResultDTO()

        self._tickers: list[TickerEntity]
        self._groups: list[GroupEntity]
        self._algorithm_configs: list[AlgorithmConfigEntity]

        self._bidirectional_ticker_group_map: BidirectionalTickerGroupMapDTO
        self._bidirectional_group_and_algo_config_map: BidirectionalGroupAlgoConfigMapDTO

    def execute(self) -> SignalEvaluationResultDTO:
        """
        Starts a full cycle of trading signal evaluation
        for all active tickers.

        Algorithm stages:
        1. Context loading <_load_context>:
        Loads all active tickers,
        then builds a bidirectional map of ticker IDs ↔ group IDs
        from each ticker's calculation configs.
        Using those group IDs, loads the active groups
        and builds a bidirectional map
        of group IDs ↔ algorithm config IDs.
        Finally, loads the active algorithm configs
        referenced by the groups.
        Raises <TickersMissingException>, <GroupsMissingException>, or
        <AlgorithmConfigsMissingException>
        if any storage returns nothing.

        2. Market-data fetch group building
        <_group_tickers_by_timeframe_and_screener>:
        Walks the algorithm config → group → ticker chain
        and groups tickers by (timeframe, screener) pair.
        Each group becomes one independent concurrent
        <get_bulk_snapshots> call in the next stage,
        so tickers sharing both attributes are batched
        while different pairs are fetched in parallel.
        Screener is part of the key because
        <get_multiple_analysis> rejects mixed-screener calls.

        3. Bulk market-data fetching
        <_get_map_of_ticker_ids_and_snapshots>:
        Submits one <get_bulk_snapshots> call per fetch group
        to the shared daemon thread pool concurrently,
        then collects results as they complete.
        Returns map of ticker IDs and market-data snapshots
        where each list contains one snapshot
        per timeframe the ticker participates in.

        4. Concurrent signal evaluation <_evaluate_signals>:
        For every ticker and signal calculation config pair,
        submits <evaluate_signal> to the thread pool.
        Each task:
        a. Calls <group.is_triggered> — AND-conjunction
        of all algorithm configs belonging
        to the group against the ticker's snapshots.
        Increments processed configs count regardless of the result.
        b. If triggered, checks the signal history
        for a recent SENT signal
        within <signal_expiration_timestamp> seconds;
        skips if one exists (deduplication guard).
        c. Persists a new historical signal (status=CREATED)
        and increments created signals count.
        d. Attempts to send a notification
        via the notification provider.
        On success sets status=SENT and increments sent signals count;
        otherwise sets status=FAILED and logs the error.
        e. Persists the signal again with the final status.
        All tasks are awaited before the method returns.

        :return: Execution statistics,
        including the number of processed evaluation configurations
        and the number of successfully created/sent signals.
        """

        self._load_context()
        logging.log(
            level=logging.INFO,
            msg=SignalEvaluatorMessagesEnum.LOADED_CONTEXT.format(count=len(self._tickers)),
        )

        tickers_by_timeframe_and_screener = self._group_tickers_by_timeframe_and_screener()
        logging.log(
            level=logging.INFO,
            msg=SignalEvaluatorMessagesEnum.GROUPED_TICKERS_BY_TIMEFRAME_AND_SCREENER,
        )

        map_of_ticker_ids_and_snapshots = self._get_map_of_ticker_ids_and_snapshots(
            tickers_by_timeframe_and_screener=tickers_by_timeframe_and_screener,
        )
        logging.log(
            level=logging.INFO,
            msg=SignalEvaluatorMessagesEnum.GENERATED_TICKER_ID_AND_SNAPSHOT_MAP,
        )

        self._evaluate_signals(map_of_ticker_ids_and_snapshots=map_of_ticker_ids_and_snapshots)

        return self._result

    def _load_context(self) -> None:
        """
        Load entity context for the trading signal evaluation algorithm.
        """

        self._tickers: list[TickerEntity] = self._ticker_repo.get_all_active()
        if not self._tickers:
            raise TickersMissingException()

        self._bidirectional_ticker_group_map = BidirectionalTickerGroupMapDTO.init_map(tickers=self._tickers)

        self._groups: list[GroupEntity] = self._group_repo.get_active_by_ids(
            ids=self._bidirectional_ticker_group_map.group_ids_and_ticker_ids.keys(),
        )
        if not self._groups:
            raise GroupsMissingException()

        self._bidirectional_group_and_algo_config_map = BidirectionalGroupAlgoConfigMapDTO.init_map(groups=self._groups)

        self._algorithm_configs: list[AlgorithmConfigEntity] = self._algo_repo.get_active_by_ids(
            ids=self._bidirectional_group_and_algo_config_map.algo_config_ids_and_group_ids.keys(),
        )
        if not self._algorithm_configs:
            raise AlgorithmConfigsMissingException()

    def _group_tickers_by_timeframe_and_screener(self) -> dict[TimeframeAndScreenerKey, list[TickerEntity]]:
        """
        Group tickers by (timeframe, screener) pair
        to form independent market-data fetch groups.

        Each entry in the returned map corresponds
        to one concurrent <get_bulk_snapshots> call,
        so tickers sharing both attributes are batched
        while different pairs are fetched in parallel.

        :return: Map of (timeframe, screener) keys to tickers.
        """

        map_of_tickers = {ticker.id: ticker for ticker in self._tickers}

        tickers_by_timeframe_and_screener: dict[TimeframeAndScreenerKey, list[TickerEntity]] = defaultdict(list)
        for algorithm_config in self._algorithm_configs:
            group_ids = self._bidirectional_group_and_algo_config_map.algo_config_ids_and_group_ids[algorithm_config.id]

            for group_id in group_ids:
                ticker_ids = self._bidirectional_ticker_group_map.group_ids_and_ticker_ids[group_id]

                for ticker_id in ticker_ids:
                    ticker = map_of_tickers[ticker_id]
                    map_key = TimeframeAndScreenerKey(
                        timeframe=algorithm_config.timeframe,
                        screener=ticker.screener,
                    )

                    tickers_by_timeframe_and_screener[map_key].append(ticker)

        return tickers_by_timeframe_and_screener

    def _get_map_of_ticker_ids_and_snapshots(
        self,
        tickers_by_timeframe_and_screener: dict[TimeframeAndScreenerKey, list[TickerEntity]],
    ) -> dict[CustomUUID, list[MarketDataSnapshotVO]]:
        """
        Retrieve market data snapshots for each ticker.

        Submits one <get_bulk_snapshots> call per fetch group
        to the thread pool concurrently,
        then merges results into a map of ticker IDs and snapshots.

        :param tickers_by_timeframe_and_screener:
        Map of (timeframe, screener) keys to tickers,
        where each entry is one independent fetch group.

        :return: Map of ticker IDs to market data snapshots,
        where each list contains one snapshot
        per timeframe the ticker participates in.
        """

        futures_to_snapshots: list[Future[dict[CustomUUID, MarketDataSnapshotVO]]] = []
        for timeframe_and_screener, tickers in tickers_by_timeframe_and_screener.items():
            future_to_snapshots = self._thread_pool.submit(
                self._market_data_provider.get_bulk_snapshots,
                tickers=tickers,
                timeframe=timeframe_and_screener.timeframe,
            )

            futures_to_snapshots.append(future_to_snapshots)

        map_of_ticker_ids_and_snapshots: dict[CustomUUID, list[MarketDataSnapshotVO]] = defaultdict(list)
        for future_to_snapshots in as_completed(futures_to_snapshots):
            map_of_ticker_ids_and_timeframe_snapshots = future_to_snapshots.result()

            for ticker_id, snapshot in map_of_ticker_ids_and_timeframe_snapshots.items():
                map_of_ticker_ids_and_snapshots[ticker_id].append(snapshot)

        return map_of_ticker_ids_and_snapshots

    def _evaluate_signals(
        self,
        map_of_ticker_ids_and_snapshots: dict[CustomUUID, list[MarketDataSnapshotVO]],
    ) -> None:
        """
        Evaluate conditions of strategies
        for each ticker's signal calculation configurations.

        :param map_of_ticker_ids_and_snapshots:
        Map of ticker IDs and ticker's market data snapshots.
        """

        def evaluate_signal(
            calculation_config: SignalCalculationConfigEntity,
            group: GroupEntity,
            algorithm_configs: list[AlgorithmConfigEntity],
            map_of_snapshots: dict[TimeframeEnum, MarketDataSnapshotVO],
        ) -> None:
            """
            Evaluate signal for a ticker.

            :param calculation_config: Signal calculation configuration.
            :param group: Group of ticker.
            :param algorithm_configs: Configurations of algorithms.
            :param map_of_snapshots: Map of timeframes and snapshots.
            """

            is_triggered = group.is_triggered(
                algorithm_configs=algorithm_configs,
                map_of_snapshots=map_of_snapshots,
            )
            with self._lock:
                self._result.processed_configs_count += 1

            if not is_triggered:
                return

            if self._history_repo.has_recent_signal(
                calculation_config_id=calculation_config.id,
                delta=timedelta(
                    seconds=calculation_config.signal_expiration_timestamp,
                ),
                status=SignalStatusEnum.SENT,
            ):
                return

            signal = HistoricalSignalEntity(calculation_config_id=calculation_config.id)
            logging.log(
                level=logging.INFO,
                msg=SignalEvaluatorMessagesEnum.DETECTED_NEW_TRADING_SIGNAL.format(signal=signal),
            )

            self._history_repo.save(signal=signal)
            with self._lock:
                self._result.created_signals_count += 1

            try:
                self._notification_provider.send_signal_alert(
                    ticker=ticker,
                    group=group,
                )

                signal_status = SignalStatusEnum.SENT
                with self._lock:
                    self._result.sent_signals_count += 1

            except FailedToSendNotificationException:
                signal_status = SignalStatusEnum.FAILED

            signal.status = signal_status
            self._history_repo.save(signal=signal)

        map_of_algorithm_configs = {
            algorithm_config.id: algorithm_config for algorithm_config in self._algorithm_configs
        }
        map_of_group_ids_and_algorithm_configs: dict[CustomUUID, list[AlgorithmConfigEntity]] = defaultdict(list)
        for (
            group_id,
            algo_config_ids,
        ) in self._bidirectional_group_and_algo_config_map.group_ids_and_algo_config_ids.items():
            for algo_config_id in algo_config_ids:
                map_of_group_ids_and_algorithm_configs[group_id].append(map_of_algorithm_configs[algo_config_id])

        map_of_groups = {group.id: group for group in self._groups}

        futures_to_signals: list[Future[None]] = []
        for ticker in self._tickers:
            map_of_snapshots = {snapshot.timeframe: snapshot for snapshot in map_of_ticker_ids_and_snapshots[ticker.id]}

            for calculation_config in ticker.calculation_configs:
                group = map_of_groups[calculation_config.group_id]
                algorithm_configs = map_of_group_ids_and_algorithm_configs[group.id]

                future_to_signal = self._thread_pool.submit(
                    evaluate_signal,
                    calculation_config=calculation_config,
                    group=group,
                    algorithm_configs=algorithm_configs,
                    map_of_snapshots=map_of_snapshots,
                )

                futures_to_signals.append(future_to_signal)

        wait(futures_to_signals)
