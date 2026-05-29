import pytest
import logging

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.boundaries import (
    DOUBLE_SHARE,
    FIFTY,
    HALF_SHARE,
    NEGATIVE_SHARE,
    ONE_HUNDRED,
    SEVENTY_FIVE,
    ZERO_STUB,
)
from src.core.domain.constants.moving_average import MovingAverageEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.strategies.envelope import (
    envelope_lower_boundary_breakout,
    envelope_upper_boundary_breakout,
)
from src.core.domain.value_objects.operational_data.indicators import IndicatorsSnapshotVO
from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO
from tests.core.domain.constants import TEST_ALGORITHM_CONFIG_TITLE, TEST_ENTITY_ID


@pytest.mark.parametrize(
    argnames=(
        "algorithm_config",
        "snapshot",
        "expected_result",
        "test_description",
    ),
    argvalues=(
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=FIFTY,
                indicators=IndicatorsSnapshotVO(SMA20=ONE_HUNDRED),
            ),
            True,
            "Price broke lower boundary (50 <= 100 * 0.5).",
            id="-lower-breakout",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=FIFTY,
                indicators=IndicatorsSnapshotVO(SMA20=SEVENTY_FIVE),
            ),
            False,
            "Price above lower boundary (50 > 75 * 0.5).",
            id="-lower-no-breakout",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=None,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=FIFTY,
                indicators=IndicatorsSnapshotVO(SMA20=ONE_HUNDRED),
            ),
            False,
            "Algorithm config is missing moving average.",
            id="-algorithm-config-missing-ma",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=None,
                indicators=IndicatorsSnapshotVO(SMA20=ONE_HUNDRED),
            ),
            False,
            "Ticker close is missing.",
            id="-ticker-close-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=FIFTY,
                indicators=IndicatorsSnapshotVO(SMA20=None),
            ),
            False,
            "Moving average value is missing.",
            id="-ma-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=NEGATIVE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ZERO_STUB,
                indicators=IndicatorsSnapshotVO(SMA20=ZERO_STUB),
            ),
            False,
            "Level is invalid for lower boundary (< 0).",
            id="-too-low-level",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ZERO_STUB,
                indicators=IndicatorsSnapshotVO(SMA20=ZERO_STUB),
            ),
            False,
            "Level is invalid for lower boundary (> 1).",
            id="-too-high-level",
        ),
    ),
)
@pytest.mark.unit
def test_envelope_lower_boundary_breakout(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result: bool = envelope_lower_boundary_breakout(
        algorithm_config=algorithm_config,
        snapshot=snapshot,
    )

    assert result == expected_result


@pytest.mark.parametrize(
    argnames=(
        "algorithm_config",
        "snapshot",
        "expected_result",
        "test_description",
    ),
    argvalues=(
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ONE_HUNDRED,
                indicators=IndicatorsSnapshotVO(SMA20=FIFTY),
            ),
            True,
            "Price broke upper boundary (100 >= 50 * 2).",
            id="-upper-breakout",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ONE_HUNDRED,
                indicators=IndicatorsSnapshotVO(SMA20=SEVENTY_FIVE),
            ),
            False,
            "Price below upper boundary (100 < 75 * 2).",
            id="-upper-no-breakout",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=None,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ONE_HUNDRED,
                indicators=IndicatorsSnapshotVO(SMA20=FIFTY),
            ),
            False,
            "Algorithm config is missing moving average.",
            id="-algorithm-config-missing-ma",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=None,
                indicators=IndicatorsSnapshotVO(SMA20=FIFTY),
            ),
            False,
            "Ticker close is missing.",
            id="-ticker-close-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=DOUBLE_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ONE_HUNDRED,
                indicators=IndicatorsSnapshotVO(SMA20=None),
            ),
            False,
            "Moving average value is missing.",
            id="-ma-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=HALF_SHARE,
                moving_average=MovingAverageEnum.SMA20,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                close=ZERO_STUB,
                indicators=IndicatorsSnapshotVO(SMA20=ZERO_STUB),
            ),
            False,
            "Level is invalid for upper boundary (< 1).",
            id="-invalid-upper-level",
        ),
    ),
)
@pytest.mark.unit
def test_envelope_upper_boundary_breakout(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result: bool = envelope_upper_boundary_breakout(
        algorithm_config=algorithm_config,
        snapshot=snapshot,
    )

    assert result == expected_result
