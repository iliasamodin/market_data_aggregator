import pytest
import logging

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.boundaries import (
    FIFTY_PERCENT,
    NEGATIVE_PERCENT,
    SEVENTY_FIVE_PERCENT,
    TWENTY_FIVE_PERCENT,
    TWO_HUNDRED_PERCENT,
    ZERO_STUB,
)
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.strategies.rsi import (
    rsi_oversold_reached,
    rsi_overbought_reached,
    rsi_growth,
    rsi_decline,
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
                algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=TWENTY_FIVE_PERCENT,
                ),
            ),
            True,
            "RSI in oversold zone (25 <= 25).",
            id="-rsi-oversold",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=FIFTY_PERCENT,
                ),
            ),
            False,
            "RSI not in oversold zone (50 > 25).",
            id="-rsi-no-oversold",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=None,
                ),
            ),
            False,
            "RSI value is missing.",
            id="-rsi-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=NEGATIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=ZERO_STUB,
                ),
            ),
            False,
            "Level is invalid for oversold zone (< 0).",
            id="-too-low-level",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERSOLD_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=SEVENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=ZERO_STUB,
                ),
            ),
            False,
            "Level is invalid for oversold zone (> 50).",
            id="-too-high-level",
        ),
    ),
)
@pytest.mark.unit
def test_rsi_oversold_reached(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result = rsi_oversold_reached(
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
                algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=SEVENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=SEVENTY_FIVE_PERCENT,
                ),
            ),
            True,
            "RSI in overbought zone (75 >= 75).",
            id="-rsi-overbought",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=SEVENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=FIFTY_PERCENT,
                ),
            ),
            False,
            "RSI not in overbought zone (50 < 75).",
            id="-rsi-no-overbought",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=SEVENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=None,
                ),
            ),
            False,
            "RSI value is missing.",
            id="-rsi-missing-val",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=ZERO_STUB,
                ),
            ),
            False,
            "Level is invalid for overbought zone (< 50).",
            id="-too-low-level",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.RSI_OVERBOUGHT_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWO_HUNDRED_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    RSI=ZERO_STUB,
                ),
            ),
            False,
            "Level is invalid for overbought zone (> 100).",
            id="-too-high-level",
        ),
    ),
)
@pytest.mark.unit
def test_rsi_overbought_reached(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result = rsi_overbought_reached(
        algorithm_config=algorithm_config,
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
                        "RSI": FIFTY_PERCENT,
                        "RSI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            True,
            "RSI is growing.",
            id="-rsi-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": TWENTY_FIVE_PERCENT,
                        "RSI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "RSI is declining.",
            id="-rsi-not-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": None,
                        "RSI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "RSI value is missing.",
            id="-rsi-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": FIFTY_PERCENT,
                        "RSI[1]": None,
                    },
                ),
            ),
            False,
            "RSI previous value is missing.",
            id="-rsi-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_rsi_growth(
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
        algorithm=AlgorithmEnum.RSI_GROWTH,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = rsi_growth(
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
                        "RSI": TWENTY_FIVE_PERCENT,
                        "RSI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            True,
            "RSI is declining.",
            id="-rsi-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": FIFTY_PERCENT,
                        "RSI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "RSI is growing.",
            id="-rsi-not-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": None,
                        "RSI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "RSI value is missing.",
            id="-rsi-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "RSI": TWENTY_FIVE_PERCENT,
                        "RSI[1]": None,
                    },
                ),
            ),
            False,
            "RSI previous value is missing.",
            id="-rsi-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_rsi_decline(
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
        algorithm=AlgorithmEnum.RSI_DECLINE,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = rsi_decline(
        algorithm_config=dummy_config,
        snapshot=snapshot,
    )

    assert result == expected_result
