import pytest
import logging

from src.core.domain.constants.boundaries import FIFTY, TWENTY_FIVE, ZERO_STUB
from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.strategies.macd import (
    macd_signal_line_bullish_crossover,
    macd_signal_line_bearish_crossover,
)
from src.core.domain.value_objects.operational_data.indicators import IndicatorsSnapshotVO
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from tests.core.domain.constants import TEST_ALGORITHM_CONFIG_TITLE, TEST_ENTITY_ID


@pytest.mark.parametrize(
    argnames=(
        "snapshot",
        "expected_result",
        "test_description",
    ),
    argvalues=(
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": FIFTY,
                        "MACD.signal": FIFTY,
                    },
                ),
            ),
            True,
            "MACD bullish crossover (macd >= signal).",
            id="-macd-bullish",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": TWENTY_FIVE,
                        "MACD.signal": FIFTY,
                    },
                ),
            ),
            False,
            "No bullish crossover (macd < signal).",
            id="-macd-no-bullish",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": None,
                        "MACD.signal": FIFTY,
                    },
                ),
            ),
            False,
            "Missing macd value.",
            id="-macd-missing-val",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": FIFTY,
                        "MACD.signal": None,
                    },
                ),
            ),
            False,
            "Missing signal value.",
            id="-signal-missing-val",
        ),
    ),
)
@pytest.mark.unit
def test_macd_signal_line_bullish_crossover(
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    dummy_config = AlgorithmConfigEntity(
        id=TEST_ENTITY_ID,
        title=TEST_ALGORITHM_CONFIG_TITLE,
        algorithm=AlgorithmEnum.MACD_SIGNAL_LINE_BULLISH_CROSSOVER,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = macd_signal_line_bullish_crossover(
        algorithm_config=dummy_config,
        snapshot=snapshot,
    )

    assert result == expected_result


@pytest.mark.parametrize(
    argnames=(
        "snapshot",
        "expected_result",
        "test_description",
    ),
    argvalues=(
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": FIFTY,
                        "MACD.signal": FIFTY,
                    },
                ),
            ),
            True,
            "MACD bearish crossover (macd <= signal).",
            id="-macd-bearish",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": FIFTY,
                        "MACD.signal": TWENTY_FIVE,
                    },
                ),
            ),
            False,
            "No bearish crossover (macd > signal).",
            id="-macd-no-bearish",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": None,
                        "MACD.signal": FIFTY,
                    },
                ),
            ),
            False,
            "Missing macd value.",
            id="-macd-missing-val",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "MACD.macd": FIFTY,
                        "MACD.signal": None,
                    },
                ),
            ),
            False,
            "Missing signal value.",
            id="-signal-missing-val",
        ),
    ),
)
@pytest.mark.unit
def test_macd_signal_line_bearish_crossover(
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    dummy_config = AlgorithmConfigEntity(
        id=TEST_ENTITY_ID,
        title=TEST_ALGORITHM_CONFIG_TITLE,
        algorithm=AlgorithmEnum.MACD_SIGNAL_LINE_BEARISH_CROSSOVER,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = macd_signal_line_bearish_crossover(
        algorithm_config=dummy_config,
        snapshot=snapshot,
    )

    assert result == expected_result
