import pytest

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.boundaries import ZERO_STUB
from src.core.domain.constants.screener import ScreenerEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.signal_calculation_config import SignalCalculationConfigEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.domain.value_objects.master_data.exchange import ExchangeVO
from src.core.domain.value_objects.operational_data.indicators import IndicatorsSnapshotVO
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO

from tests.utils import generate_mock_uuid

# Shared IDs

# Tickers
TICKER_1_ID = generate_mock_uuid(1)  # BTCUSDT — linked to both groups
TICKER_2_ID = generate_mock_uuid(2)  # ETHUSDT — linked to Group 1 only
TICKER_3_ID = generate_mock_uuid(3)  # SOLUSDT — linked to Group 2 only

# Groups (AND-conjunction of algorithm configs)
# RSI oversold AND ADX +DI growing (1W)
GROUP_1_ID = generate_mock_uuid(4)
# MACD bullish AND RSI overbought (4H)
GROUP_2_ID = generate_mock_uuid(5)

# Algorithm configs
# RSI_OVERSOLD_REACHED, 1W — in Group 1
ALGO_CONFIG_1_ID = generate_mock_uuid(6)
# ADX_POS_DI_GROWTH, 1W — in Group 1
ALGO_CONFIG_2_ID = generate_mock_uuid(7)
# MACD_SIGNAL_LINE_BULLISH_CROSSOVER, 4H — in Group 2
ALGO_CONFIG_3_ID = generate_mock_uuid(8)
# RSI_OVERBOUGHT_REACHED, 4H — in Group 2
ALGO_CONFIG_4_ID = generate_mock_uuid(9)

# Calculation configs (ticker ↔ group links)
CALC_CONFIG_1_ID = generate_mock_uuid(10)  # TICKER_1 → GROUP_1
CALC_CONFIG_2_ID = generate_mock_uuid(11)  # TICKER_1 → GROUP_2
CALC_CONFIG_3_ID = generate_mock_uuid(12)  # TICKER_2 → GROUP_1
CALC_CONFIG_4_ID = generate_mock_uuid(13)  # TICKER_3 → GROUP_2

# Group 3: cross-timeframe AND (RSI 1W + MACD 4H)
# RSI oversold (1W) AND MACD bullish (4H)
GROUP_3_ID = generate_mock_uuid(14)
CALC_CONFIG_5_ID = generate_mock_uuid(15)  # TICKER_2 → GROUP_3

# Indicator values used to construct snapshots

# Group 1 thresholds (1W)
RSI_OVERSOLD_LEVEL = 25.0
RSI_OVERSOLD_VALUE = 20.0  # ≤ 25 → RSI_OVERSOLD_REACHED fires
# Neither oversold nor overbought (25 < 50 < 75)
RSI_NEUTRAL_VALUE = 50.0

ADX_POS_DI_RISING = 30.0  # Current +DI
# Current +DI == previous → ADX_POS_DI_GROWTH does NOT fire
ADX_POS_DI_FLAT = 25.0
ADX_POS_DI_PREV = 25.0  # Previous +DI (< RISING → growth detected)

# Group 2 thresholds (4H)
RSI_OVERBOUGHT_LEVEL = 75.0
RSI_OVERBOUGHT_VALUE = 80.0  # ≥ 75 → RSI_OVERBOUGHT_REACHED fires

MACD_ABOVE_SIGNAL = 100.0  # MACD fast line
# Signal line; MACD ≥ signal → MACD_BULLISH fires
MACD_SIGNAL_VALUE = 50.0
# MACD fast line < signal → MACD_BULLISH does NOT fire
MACD_BELOW_SIGNAL = 30.0

SIGNAL_EXPIRATION_SECONDS = 3600.0

# Expected outcome counts used in test assertions

# Number of calc_configs processed
# (Equals the number of ticker-to-group links evaluated)
ONE_CONFIG_PROCESSED = 1  # Single ticker with one calc_config
# Ticker_1 (2 configs) or two tickers with one config each
TWO_CONFIGS_PROCESSED = 2
# Full scenario: ticker_1(2) + ticker_2(1) + ticker_3(1)
FOUR_CONFIGS_PROCESSED = 4

# Signal counts: created / sent / persisted in history
NO_SIGNALS = 0
ONE_SIGNAL = 1
TWO_SIGNALS = 2
FOUR_SIGNALS = 4


# Snapshot factories
# (Module-level helpers; call with any ticker_id inside tests)


def make_snapshot_1w_g1_fires(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    RSI ≤ 25 AND ADX +DI growing → both Group 1 conditions met.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        indicators=IndicatorsSnapshotVO(
            **{
                "RSI": RSI_OVERSOLD_VALUE,
                "ADX+DI": ADX_POS_DI_RISING,
                "ADX+DI[1]": ADX_POS_DI_PREV,
            }
        ),
    )

    return snapshot


def make_snapshot_1w_rsi_fails(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    RSI > 25 → RSI_OVERSOLD condition fails; ADX still grows.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        indicators=IndicatorsSnapshotVO(
            **{
                "RSI": RSI_NEUTRAL_VALUE,
                "ADX+DI": ADX_POS_DI_RISING,
                "ADX+DI[1]": ADX_POS_DI_PREV,
            }
        ),
    )

    return snapshot


def make_snapshot_1w_adx_fails(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    RSI ≤ 25 but ADX +DI flat → ADX_POS_DI_GROWTH condition fails.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        indicators=IndicatorsSnapshotVO(
            **{
                "RSI": RSI_OVERSOLD_VALUE,
                "ADX+DI": ADX_POS_DI_FLAT,
                "ADX+DI[1]": ADX_POS_DI_PREV,
            }
        ),
    )

    return snapshot


def make_snapshot_4h_g2_fires(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    MACD ≥ signal AND RSI ≥ 75 → both Group 2 conditions met.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_4_HOURS,
        indicators=IndicatorsSnapshotVO(
            **{
                "MACD.macd": MACD_ABOVE_SIGNAL,
                "MACD.signal": MACD_SIGNAL_VALUE,
                "RSI": RSI_OVERBOUGHT_VALUE,
            }
        ),
    )

    return snapshot


def make_snapshot_4h_rsi_fails(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    MACD ≥ signal but RSI < 75 → RSI_OVERBOUGHT condition fails.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_4_HOURS,
        indicators=IndicatorsSnapshotVO(
            **{
                "MACD.macd": MACD_ABOVE_SIGNAL,
                "MACD.signal": MACD_SIGNAL_VALUE,
                "RSI": RSI_NEUTRAL_VALUE,
            }
        ),
    )

    return snapshot


def make_snapshot_4h_macd_fails(ticker_id: CustomUUID) -> MarketDataSnapshotVO:
    """
    MACD < signal → MACD_BULLISH condition fails.
    """

    snapshot = MarketDataSnapshotVO(
        ticker_id=ticker_id,
        timeframe=TimeframeEnum.INTERVAL_4_HOURS,
        indicators=IndicatorsSnapshotVO(
            **{
                "MACD.macd": MACD_BELOW_SIGNAL,
                "MACD.signal": MACD_SIGNAL_VALUE,
                "RSI": RSI_OVERBOUGHT_VALUE,
            }
        ),
    )

    return snapshot


# Algorithm config fixtures


@pytest.fixture
def algo_config_rsi_oversold_1w() -> AlgorithmConfigEntity:
    """
    RSI_OVERSOLD_REACHED on 1W — fires when RSI ≤ 25.
    """

    algorithm_config = AlgorithmConfigEntity(
        id=ALGO_CONFIG_1_ID,
        title="RSI Oversold 1W",
        algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=RSI_OVERSOLD_LEVEL,
    )

    return algorithm_config


@pytest.fixture
def algo_config_adx_bullish_1w() -> AlgorithmConfigEntity:
    """
    ADX_POS_DI_GROWTH on 1W — fires when +DI is growing.
    """

    algorithm_config = AlgorithmConfigEntity(
        id=ALGO_CONFIG_2_ID,
        title="ADX Bullish 1W",
        algorithm=AlgorithmEnum.ADX_POS_DI_GROWTH,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )

    return algorithm_config


@pytest.fixture
def algo_config_macd_bullish_4h() -> AlgorithmConfigEntity:
    """
    MACD_SIGNAL_LINE_BULLISH_CROSSOVER on 4H — fires when MACD ≥ signal.
    """

    algorithm_config = AlgorithmConfigEntity(
        id=ALGO_CONFIG_3_ID,
        title="MACD Bullish 4H",
        algorithm=AlgorithmEnum.MACD_SIGNAL_LINE_BULLISH_CROSSOVER,
        timeframe=TimeframeEnum.INTERVAL_4_HOURS,
        level=ZERO_STUB,
    )

    return algorithm_config


@pytest.fixture
def algo_config_rsi_overbought_4h() -> AlgorithmConfigEntity:
    """
    RSI_OVERBOUGHT_REACHED on 4H — fires when RSI ≥ 75.
    """

    algorithm_config = AlgorithmConfigEntity(
        id=ALGO_CONFIG_4_ID,
        title="RSI Overbought 4H",
        algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
        timeframe=TimeframeEnum.INTERVAL_4_HOURS,
        level=RSI_OVERBOUGHT_LEVEL,
    )

    return algorithm_config


# Group fixtures


@pytest.fixture
def group_1() -> GroupEntity:
    """
    AND-group: RSI oversold AND ADX +DI growing (both on 1W).
    """

    group = GroupEntity(
        id=GROUP_1_ID,
        title="RSI Oversold + ADX Bullish 1W",
        description="Fires when RSI reaches the oversold zone AND ADX +DI is growing on the weekly timeframe.",
        algorithm_config_ids=[
            ALGO_CONFIG_1_ID,
            ALGO_CONFIG_2_ID,
        ],
    )

    return group


@pytest.fixture
def group_2() -> GroupEntity:
    """
    AND-group: MACD bullish crossover AND RSI overbought (both on 4H).
    """

    group = GroupEntity(
        id=GROUP_2_ID,
        title="MACD Bullish + RSI Overbought 4H",
        description=(
            "Fires when MACD crosses above the signal line AND RSI reaches the overbought zone on the 4-hour timeframe."
        ),
        algorithm_config_ids=[
            ALGO_CONFIG_3_ID,
            ALGO_CONFIG_4_ID,
        ],
    )

    return group


# Calculation config fixtures


@pytest.fixture
def calc_config_1() -> SignalCalculationConfigEntity:
    """
    Links TICKER_1 to GROUP_1.
    """

    calc_config = SignalCalculationConfigEntity(
        id=CALC_CONFIG_1_ID,
        group_id=GROUP_1_ID,
        signal_expiration_timestamp=SIGNAL_EXPIRATION_SECONDS,
    )

    return calc_config


@pytest.fixture
def calc_config_2() -> SignalCalculationConfigEntity:
    """
    Links TICKER_1 to GROUP_2.
    """

    calc_config = SignalCalculationConfigEntity(
        id=CALC_CONFIG_2_ID,
        group_id=GROUP_2_ID,
        signal_expiration_timestamp=SIGNAL_EXPIRATION_SECONDS,
    )

    return calc_config


@pytest.fixture
def calc_config_3() -> SignalCalculationConfigEntity:
    """
    Links TICKER_2 to GROUP_1.
    """

    calc_config = SignalCalculationConfigEntity(
        id=CALC_CONFIG_3_ID,
        group_id=GROUP_1_ID,
        signal_expiration_timestamp=SIGNAL_EXPIRATION_SECONDS,
    )

    return calc_config


@pytest.fixture
def calc_config_4() -> SignalCalculationConfigEntity:
    """
    Links TICKER_3 to GROUP_2.
    """

    calc_config = SignalCalculationConfigEntity(
        id=CALC_CONFIG_4_ID,
        group_id=GROUP_2_ID,
        signal_expiration_timestamp=SIGNAL_EXPIRATION_SECONDS,
    )

    return calc_config


# Ticker fixtures


@pytest.fixture
def ticker_1(
    calc_config_1: SignalCalculationConfigEntity,
    calc_config_2: SignalCalculationConfigEntity,
) -> TickerEntity:
    """
    BTCUSDT — participates in Group 1 (1W) and Group 2 (4H).
    """

    ticker = TickerEntity(
        id=TICKER_1_ID,
        title="BTCUSDT",
        key="BTCUSDT",
        screener=ScreenerEnum.CRYPTO,
        exchange=ExchangeVO(
            title="BINANCE",
            key="BINANCE",
        ),
        calculation_configs=[
            calc_config_1,
            calc_config_2,
        ],
    )

    return ticker


@pytest.fixture
def ticker_2(calc_config_3: SignalCalculationConfigEntity) -> TickerEntity:
    """
    ETHUSDT — participates in Group 1 (1W) only.
    """

    ticker = TickerEntity(
        id=TICKER_2_ID,
        title="ETHUSDT",
        key="ETHUSDT",
        screener=ScreenerEnum.CRYPTO,
        exchange=ExchangeVO(
            title="BINANCE",
            key="BINANCE",
        ),
        calculation_configs=[
            calc_config_3,
        ],
    )

    return ticker


@pytest.fixture
def ticker_3(calc_config_4: SignalCalculationConfigEntity) -> TickerEntity:
    """
    SOLUSDT — participates in Group 2 (4H) only.
    """

    ticker = TickerEntity(
        id=TICKER_3_ID,
        title="SOLUSDT",
        key="SOLUSDT",
        screener=ScreenerEnum.CRYPTO,
        exchange=ExchangeVO(
            title="BINANCE",
            key="BINANCE",
        ),
        calculation_configs=[
            calc_config_4,
        ],
    )

    return ticker


# Group 3: cross-timeframe AND (RSI oversold on 1W + MACD bullish on 4H)


@pytest.fixture
def group_3() -> GroupEntity:
    """
    AND-group mixing timeframes:
    RSI oversold (1W) AND MACD bullish (4H).
    """

    group = GroupEntity(
        id=GROUP_3_ID,
        title="RSI Oversold 1W + MACD Bullish 4H",
        description=(
            "Fires when RSI reaches the oversold zone on the weekly timeframe "
            "AND MACD crosses above the signal line on the 4-hour timeframe."
        ),
        algorithm_config_ids=[
            ALGO_CONFIG_1_ID,
            ALGO_CONFIG_3_ID,
        ],
    )

    return group


@pytest.fixture
def calc_config_5() -> SignalCalculationConfigEntity:
    """
    Links TICKER_2 to GROUP_3 (cross-timeframe).
    """

    calc_config = SignalCalculationConfigEntity(
        id=CALC_CONFIG_5_ID,
        group_id=GROUP_3_ID,
        signal_expiration_timestamp=SIGNAL_EXPIRATION_SECONDS,
    )

    return calc_config


@pytest.fixture
def ticker_for_group_3(calc_config_5: SignalCalculationConfigEntity) -> TickerEntity:
    """
    ETHUSDT — participates only in the cross-timeframe Group 3.
    """

    ticker = TickerEntity(
        id=TICKER_2_ID,
        title="ETHUSDT",
        key="ETHUSDT",
        screener=ScreenerEnum.CRYPTO,
        exchange=ExchangeVO(
            title="BINANCE",
            key="BINANCE",
        ),
        calculation_configs=[
            calc_config_5,
        ],
    )

    return ticker
