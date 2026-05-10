from collections.abc import Callable

import logging
import pytest

from src.core.application.exceptions.signal_evaluator import (
    AlgorithmConfigsMissingException,
    GroupsMissingException,
    TickersMissingException,
)
from src.core.application.use_cases.signal_evaluator import SignalEvaluatorUseCase
from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.signal_history import HistoricalSignalEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from src.core.domain.utils.custom_uuid import CustomUUID

from tests.core.application.use_cases.conftest import (
    TICKER_1_ID,
    TICKER_2_ID,
    TICKER_3_ID,
    CALC_CONFIG_1_ID,
    CALC_CONFIG_2_ID,
    CALC_CONFIG_3_ID,
    CALC_CONFIG_4_ID,
    CALC_CONFIG_5_ID,
    ONE_CONFIG_PROCESSED,
    TWO_CONFIGS_PROCESSED,
    FOUR_CONFIGS_PROCESSED,
    ONE_SIGNAL,
    TWO_SIGNALS,
    FOUR_SIGNALS,
    NO_SIGNALS,
    make_snapshot_1w_g1_fires,
    make_snapshot_1w_rsi_fails,
    make_snapshot_1w_adx_fails,
    make_snapshot_4h_g2_fires,
    make_snapshot_4h_rsi_fails,
    make_snapshot_4h_macd_fails,
)
from tests.core.application.use_cases.mocks.algorithm_config_repository import InMemoryAlgorithmConfigRepository
from tests.core.application.use_cases.mocks.group_repository import InMemoryGroupRepository
from tests.core.application.use_cases.mocks.market_data_provider import InMemoryMarketDataProvider
from tests.core.application.use_cases.mocks.notification_provider import InMemoryNotificationProvider
from tests.core.application.use_cases.mocks.signal_history_repository import InMemorySignalHistoryRepository
from tests.core.application.use_cases.mocks.ticker_repository import InMemoryTickerRepository


@pytest.mark.integration
class TestSignalEvaluatorUseCase:
    """
    Integration tests for <SignalEvaluatorUseCase>.

    Algorithm and signal calculation configurations
    are for testing purposes only
    and are not intended for real trading signal calculations.
    """

    @staticmethod
    def _make_use_case(
        ticker_repo: InMemoryTickerRepository,
        group_repo: InMemoryGroupRepository,
        algo_repo: InMemoryAlgorithmConfigRepository,
        history_repo: InMemorySignalHistoryRepository,
        market_data_provider: InMemoryMarketDataProvider,
        notification_provider: InMemoryNotificationProvider,
    ) -> SignalEvaluatorUseCase:
        use_case = SignalEvaluatorUseCase(
            ticker_repo=ticker_repo,
            group_repo=group_repo,
            algorithm_repo=algo_repo,
            signal_history_repo=history_repo,
            market_data_provider=market_data_provider,
            notification_provider=notification_provider,
        )

        return use_case

    # Successful, simple: single ticker, single group, single timeframe

    @pytest.mark.parametrize(
        argnames=(
            "snapshot_factory",
            "expected_created",
            "expected_sent",
            "expected_calc_config_id",
            "test_description",
        ),
        argvalues=(
            pytest.param(
                make_snapshot_1w_g1_fires,
                ONE_SIGNAL,
                ONE_SIGNAL,
                CALC_CONFIG_3_ID,
                "ETHUSDT linked to Group 1 (RSI_OVERSOLD + ADX_POS_DI_GROWTH, 1W) via calc_config_3; "
                "both conditions met (RSI ≤ 25, +DI growing). "
                "Expected: one signal created and sent, status SENT in history.",
                id="-all-conditions-met",
            ),
            pytest.param(
                make_snapshot_1w_rsi_fails,
                NO_SIGNALS,
                NO_SIGNALS,
                None,
                "ETHUSDT linked to Group 1 (RSI_OVERSOLD + ADX_POS_DI_GROWTH, 1W) via calc_config_3; "
                "RSI is neutral (> 25), condition not met. "
                "Expected: no signal created or sent, history stays empty.",
                id="-rsi-condition-fails",
            ),
            pytest.param(
                make_snapshot_1w_adx_fails,
                NO_SIGNALS,
                NO_SIGNALS,
                None,
                "ETHUSDT linked to Group 1 (RSI_OVERSOLD + ADX_POS_DI_GROWTH, 1W) via calc_config_3; "
                "RSI ≤ 25 but ADX +DI flat (no growth). "
                "Expected: no signal created or sent, history stays empty.",
                id="-adx-condition-fails",
            ),
        ),
    )
    def test_execute_and_group_1w(
        self,
        ticker_2: TickerEntity,
        group_1: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
        snapshot_factory: Callable[[CustomUUID], MarketDataSnapshotVO],
        expected_created: int,
        expected_sent: int,
        expected_calc_config_id: CustomUUID | None,
        test_description: str,
    ) -> None:
        """
        Single ticker: RSI_OVERSOLD AND ADX_POS_DI_GROWTH on 1W.
        """

        logging.log(level=logging.INFO, msg=test_description)

        history_repo = InMemorySignalHistoryRepository()
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2]),
            group_repo=InMemoryGroupRepository(groups=[group_1]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[algo_config_rsi_oversold_1w, algo_config_adx_bullish_1w],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={TICKER_2_ID: {TimeframeEnum.INTERVAL_1_WEEK: snapshot_factory(TICKER_2_ID)}},
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()
        saved = history_repo.signals

        assert result.processed_configs_count == ONE_CONFIG_PROCESSED
        assert result.created_signals_count == expected_created
        assert result.sent_signals_count == expected_sent
        assert len(saved) == expected_created
        assert len(notification_provider.sent_alerts) == expected_sent

        if expected_calc_config_id is not None:
            assert saved[0].status == SignalStatusEnum.SENT
            assert saved[0].calculation_config_id == expected_calc_config_id

    # Successful, complex: AND-group spanning multiple timeframes

    @pytest.mark.parametrize(
        argnames=(
            "snapshot_factory_4h",
            "expected_created",
            "expected_sent",
            "expected_calc_config_id",
            "test_description",
        ),
        argvalues=(
            pytest.param(
                make_snapshot_4h_g2_fires,
                ONE_SIGNAL,
                ONE_SIGNAL,
                CALC_CONFIG_5_ID,
                "ETHUSDT linked to Group 3 (RSI_OVERSOLD 1W + MACD_BULLISH 4H) via calc_config_5; "
                "both timeframe conditions satisfied. "
                "Expected: one signal created and sent, status SENT in history.",
                id="-all-conditions-met",
            ),
            pytest.param(
                make_snapshot_4h_macd_fails,
                NO_SIGNALS,
                NO_SIGNALS,
                None,
                "ETHUSDT linked to Group 3 (RSI_OVERSOLD 1W + MACD_BULLISH 4H) via calc_config_5; "
                "RSI fires on 1W, MACD fails on 4H. "
                "Expected: no signal created or sent, history stays empty.",
                id="-4h-condition-fails",
            ),
        ),
    )
    def test_execute_and_group_mixed_timeframes(
        self,
        ticker_for_group_3: TickerEntity,
        group_3: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_macd_bullish_4h: AlgorithmConfigEntity,
        snapshot_factory_4h: Callable[[CustomUUID], MarketDataSnapshotVO],
        expected_created: int,
        expected_sent: int,
        expected_calc_config_id: CustomUUID | None,
        test_description: str,
    ) -> None:
        """
        AND-group: RSI_OVERSOLD (1W) AND MACD_BULLISH (4H).
        """

        logging.log(level=logging.INFO, msg=test_description)

        history_repo = InMemorySignalHistoryRepository()
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_for_group_3]),
            group_repo=InMemoryGroupRepository(groups=[group_3]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[algo_config_rsi_oversold_1w, algo_config_macd_bullish_4h],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={
                    TICKER_2_ID: {
                        TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_2_ID),
                        TimeframeEnum.INTERVAL_4_HOURS: snapshot_factory_4h(TICKER_2_ID),
                    },
                },
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()
        saved = history_repo.signals

        assert result.processed_configs_count == ONE_CONFIG_PROCESSED
        assert result.created_signals_count == expected_created
        assert result.sent_signals_count == expected_sent
        assert len(saved) == expected_created
        assert len(notification_provider.sent_alerts) == expected_sent

        if expected_calc_config_id is not None:
            assert saved[0].status == SignalStatusEnum.SENT
            assert saved[0].calculation_config_id == expected_calc_config_id

    def test_execute_ticker_with_two_groups_cross_timeframe(
        self,
        ticker_1: TickerEntity,
        group_1: GroupEntity,
        group_2: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
        algo_config_macd_bullish_4h: AlgorithmConfigEntity,
        algo_config_rsi_overbought_4h: AlgorithmConfigEntity,
    ) -> None:
        """
        BTCUSDT has two calc_configs:
            Config 1 → Group 1 (1W): RSI fires, ADX fires → sent.
            Config 2 → Group 2 (4H): MACD fires, RSI not met → none.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "BTCUSDT has cc1 → Group 1 (1W) and cc2 → Group 2 (4H). "
                "Group 1 fires (RSI + ADX met), Group 2 does not (RSI overbought not met). "
                "Expected: one SENT signal for cc1; processed_configs=2."
            ),
        )

        history_repo = InMemorySignalHistoryRepository()
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_1]),
            group_repo=InMemoryGroupRepository(groups=[group_1, group_2]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[
                    algo_config_rsi_oversold_1w,
                    algo_config_adx_bullish_1w,
                    algo_config_macd_bullish_4h,
                    algo_config_rsi_overbought_4h,
                ],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={
                    TICKER_1_ID: {
                        TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_1_ID),
                        TimeframeEnum.INTERVAL_4_HOURS: make_snapshot_4h_rsi_fails(TICKER_1_ID),
                    },
                },
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()

        assert result.processed_configs_count == TWO_CONFIGS_PROCESSED
        assert result.created_signals_count == ONE_SIGNAL
        assert result.sent_signals_count == ONE_SIGNAL

        saved = history_repo.signals

        assert len(saved) == ONE_SIGNAL
        assert saved[0].status == SignalStatusEnum.SENT
        assert saved[0].calculation_config_id == CALC_CONFIG_1_ID

        assert len(notification_provider.sent_alerts) == ONE_SIGNAL

    def test_execute_multiple_tickers_sharing_group_independent_evaluation(
        self,
        ticker_2: TickerEntity,
        ticker_3: TickerEntity,
        group_1: GroupEntity,
        group_2: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
        algo_config_macd_bullish_4h: AlgorithmConfigEntity,
        algo_config_rsi_overbought_4h: AlgorithmConfigEntity,
    ) -> None:
        """
        ETHUSDT (Group 1) and SOLUSDT (Group 2) evaluated independently:
        ETHUSDT: Group 1 fires (RSI + ADX on 1W) → signal sent.
        SOLUSDT: Group 2 fires (MACD + RSI overbought, 4H) → sent.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "ETHUSDT → Group 1 (1W) and SOLUSDT → Group 2 (4H); both fire. "
                "Two tickers evaluated independently in a single run. "
                "Expected: two SENT signals, one each for cc3 and cc4."
            ),
        )

        history_repo = InMemorySignalHistoryRepository()
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2, ticker_3]),
            group_repo=InMemoryGroupRepository(groups=[group_1, group_2]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[
                    algo_config_rsi_oversold_1w,
                    algo_config_adx_bullish_1w,
                    algo_config_macd_bullish_4h,
                    algo_config_rsi_overbought_4h,
                ],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={
                    TICKER_2_ID: {TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_2_ID)},
                    TICKER_3_ID: {TimeframeEnum.INTERVAL_4_HOURS: make_snapshot_4h_g2_fires(TICKER_3_ID)},
                },
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()

        assert result.processed_configs_count == TWO_CONFIGS_PROCESSED
        assert result.created_signals_count == TWO_SIGNALS
        assert result.sent_signals_count == TWO_SIGNALS

        saved_ids = {signal.calculation_config_id for signal in history_repo.signals}

        assert saved_ids == {CALC_CONFIG_3_ID, CALC_CONFIG_4_ID}
        assert all(signal.status == SignalStatusEnum.SENT for signal in history_repo.signals)

    def test_execute_full_scenario_multiple_tickers_groups_and_timeframes(
        self,
        ticker_1: TickerEntity,
        ticker_2: TickerEntity,
        ticker_3: TickerEntity,
        group_1: GroupEntity,
        group_2: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
        algo_config_macd_bullish_4h: AlgorithmConfigEntity,
        algo_config_rsi_overbought_4h: AlgorithmConfigEntity,
    ) -> None:
        """
        Full integration: 3 tickers, 2 groups, 4 configs, 2 timeframes.

        Evaluation matrix (calc_config → group → outcome):
            BTCUSDT / cc1 → Group 1 (1W): RSI fires, ADX fires → SENT
            BTCUSDT / cc2 → Group 2 (4H): MACD fires, RSI fires → SENT
            ETHUSDT / cc3 → Group 1 (1W): RSI fires, ADX fires → SENT
            SOLUSDT / cc4 → Group 2 (4H): MACD fires, RSI fires → SENT

        Expected: processed=4, created=4, sent=4.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "Three tickers, two groups, four calc_configs, two timeframes; "
                "all conditions fire across cc1–cc4. "
                "Expected: processed=4, created=4, sent=4; all signals SENT."
            ),
        )

        history_repo = InMemorySignalHistoryRepository()
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_1, ticker_2, ticker_3]),
            group_repo=InMemoryGroupRepository(groups=[group_1, group_2]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[
                    algo_config_rsi_oversold_1w,
                    algo_config_adx_bullish_1w,
                    algo_config_macd_bullish_4h,
                    algo_config_rsi_overbought_4h,
                ],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={
                    TICKER_1_ID: {
                        TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_1_ID),
                        TimeframeEnum.INTERVAL_4_HOURS: make_snapshot_4h_g2_fires(TICKER_1_ID),
                    },
                    TICKER_2_ID: {
                        TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_2_ID),
                    },
                    TICKER_3_ID: {
                        TimeframeEnum.INTERVAL_4_HOURS: make_snapshot_4h_g2_fires(TICKER_3_ID),
                    },
                },
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()

        assert result.processed_configs_count == FOUR_CONFIGS_PROCESSED
        assert result.created_signals_count == FOUR_SIGNALS
        assert result.sent_signals_count == FOUR_SIGNALS

        saved_ids = {signal.calculation_config_id for signal in history_repo.signals}

        assert saved_ids == {CALC_CONFIG_1_ID, CALC_CONFIG_2_ID, CALC_CONFIG_3_ID, CALC_CONFIG_4_ID}
        assert all(signal.status == SignalStatusEnum.SENT for signal in history_repo.signals)

        assert len(notification_provider.sent_alerts) == FOUR_SIGNALS

    # Unsuccessful: signal blocked or notification failed

    def test_execute_deduplication_blocks_signal_for_active_expiration(
        self,
        ticker_2: TickerEntity,
        group_1: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
        calc_config_3,
    ) -> None:
        """
        Group 1 fires for ETHUSDT, but a SENT signal for calc_config_3
        already exists within the window → no new signal created.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "ETHUSDT → Group 1 via cc3; a SENT signal for cc3 "
                "pre-exists in history within the active expiration window. "
                "Expected: no new signal created; history stays at one signal."
            ),
        )

        recent_sent = HistoricalSignalEntity(
            calculation_config_id=calc_config_3.id,
            status=SignalStatusEnum.SENT,
        )
        history_repo = InMemorySignalHistoryRepository(signals=[recent_sent])
        notification_provider = InMemoryNotificationProvider()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2]),
            group_repo=InMemoryGroupRepository(groups=[group_1]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[algo_config_rsi_oversold_1w, algo_config_adx_bullish_1w],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={TICKER_2_ID: {TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_2_ID)}},
            ),
            notification_provider=notification_provider,
        )

        result = use_case.execute()

        assert result.processed_configs_count == ONE_CONFIG_PROCESSED
        assert result.created_signals_count == NO_SIGNALS
        assert result.sent_signals_count == NO_SIGNALS
        # Only the pre-existing signal
        assert len(history_repo.signals) == ONE_SIGNAL
        assert notification_provider.sent_alerts == []

    def test_execute_notification_failure_saves_signal_as_failed(
        self,
        ticker_2: TickerEntity,
        group_1: GroupEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
    ) -> None:
        """
        Group 1 fires for ETHUSDT, notification provider raises → signal
        is created (FAILED) but sent_signals_count stays at 0.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "ETHUSDT → Group 1; notification provider configured to raise. "
                "Group 1 conditions fire; signal creation succeeds, delivery fails. "
                "Expected: one FAILED signal in history; sent_signals_count=0."
            ),
        )

        history_repo = InMemorySignalHistoryRepository()

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2]),
            group_repo=InMemoryGroupRepository(groups=[group_1]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[algo_config_rsi_oversold_1w, algo_config_adx_bullish_1w],
            ),
            history_repo=history_repo,
            market_data_provider=InMemoryMarketDataProvider(
                map_of_snapshots={TICKER_2_ID: {TimeframeEnum.INTERVAL_1_WEEK: make_snapshot_1w_g1_fires(TICKER_2_ID)}},
            ),
            notification_provider=InMemoryNotificationProvider(should_fail=True),
        )

        result = use_case.execute()

        assert result.processed_configs_count == ONE_CONFIG_PROCESSED
        assert result.created_signals_count == ONE_SIGNAL
        assert result.sent_signals_count == NO_SIGNALS

        saved = history_repo.signals

        assert len(saved) == ONE_SIGNAL
        assert saved[0].status == SignalStatusEnum.FAILED

    # Guard tests: context-loading exceptions

    def test_execute_raises_when_no_tickers(self) -> None:
        """
        Ticker repository is empty; no tickers are registered.
        Use case raises TickersMissingException immediately.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "Ticker repository is empty; no tickers registered. "
                "Use case execute() called with no data to process. "
                "Expected: TickersMissingException raised."
            ),
        )

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[]),
            group_repo=InMemoryGroupRepository(),
            algo_repo=InMemoryAlgorithmConfigRepository(),
            history_repo=InMemorySignalHistoryRepository(),
            market_data_provider=InMemoryMarketDataProvider(),
            notification_provider=InMemoryNotificationProvider(),
        )

        with pytest.raises(TickersMissingException):
            use_case.execute()

    def test_execute_raises_when_no_groups(
        self,
        ticker_2: TickerEntity,
        algo_config_rsi_oversold_1w: AlgorithmConfigEntity,
        algo_config_adx_bullish_1w: AlgorithmConfigEntity,
    ) -> None:
        """
        ETHUSDT ticker is registered; group repository is empty.
        Use case raises GroupsMissingException after loading tickers.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "ETHUSDT ticker registered; group repository is empty. "
                "Use case proceeds past ticker loading, fails at group loading. "
                "Expected: GroupsMissingException raised."
            ),
        )

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2]),
            group_repo=InMemoryGroupRepository(groups=[]),
            algo_repo=InMemoryAlgorithmConfigRepository(
                algorithm_configs=[algo_config_rsi_oversold_1w, algo_config_adx_bullish_1w],
            ),
            history_repo=InMemorySignalHistoryRepository(),
            market_data_provider=InMemoryMarketDataProvider(),
            notification_provider=InMemoryNotificationProvider(),
        )

        with pytest.raises(GroupsMissingException):
            use_case.execute()

    def test_execute_raises_when_no_algorithm_configs(
        self,
        ticker_2: TickerEntity,
        group_1: GroupEntity,
    ) -> None:
        """
        ETHUSDT and Group 1 are registered; algo config repository is empty.
        Use case raises AlgorithmConfigsMissingException after loading groups.
        """

        logging.log(
            level=logging.INFO,
            msg=(
                "ETHUSDT and Group 1 registered; algo config repository is empty. "
                "Use case fails at algorithm config loading. "
                "Expected: AlgorithmConfigsMissingException raised."
            ),
        )

        use_case = self._make_use_case(
            ticker_repo=InMemoryTickerRepository(tickers=[ticker_2]),
            group_repo=InMemoryGroupRepository(groups=[group_1]),
            algo_repo=InMemoryAlgorithmConfigRepository(algorithm_configs=[]),
            history_repo=InMemorySignalHistoryRepository(),
            market_data_provider=InMemoryMarketDataProvider(),
            notification_provider=InMemoryNotificationProvider(),
        )

        with pytest.raises(AlgorithmConfigsMissingException):
            use_case.execute()
