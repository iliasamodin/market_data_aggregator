import pytest
import logging

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.boundaries import (
    FIFTY_PERCENT,
    NEGATIVE_PERCENT,
    TWENTY_FIVE_PERCENT,
    TWO_HUNDRED_PERCENT,
    ZERO_PERCENT,
    ZERO_STUB,
)
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.strategies.adx import (
    adx_consolidation_stage_transition,
    adx_di_bearish_crossover,
    adx_di_bullish_crossover,
    adx_extreme_trend_reached,
    adx_neg_di_decline,
    adx_neg_di_growth,
    adx_pos_di_decline,
    adx_pos_di_growth,
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
                algorithm=AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=TWENTY_FIVE_PERCENT),
            ),
            True,
            "Trend has entered the consolidation stage (ADX == level).",
            id="-entered-consolidation-stage",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=FIFTY_PERCENT),
            ),
            False,
            "Trend not entered the consolidation stage (ADX > level).",
            id="-not-entered-consolidation-stage",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWENTY_FIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=None),
            ),
            False,
            "No ADX value provided.",
            id="-no-adx",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=NEGATIVE_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=TWENTY_FIVE_PERCENT),
            ),
            False,
            "Level is invalid for consolidation stage (< 0).",
            id="-too-low-level",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=FIFTY_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=TWENTY_FIVE_PERCENT),
            ),
            False,
            "Level is invalid for consolidation stage (> 25).",
            id="-too-high-level",
        ),
    ),
)
@pytest.mark.unit
def test_adx_consolidation_stage_transition(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result: bool = adx_consolidation_stage_transition(
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
                algorithm=AlgorithmEnum.ADX_EXTREME_TREND_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=FIFTY_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=FIFTY_PERCENT),
            ),
            True,
            "Trend reached extreme stage (ADX == level).",
            id="-extreme-reached",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_EXTREME_TREND_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=FIFTY_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=TWENTY_FIVE_PERCENT),
            ),
            False,
            "Trend not reached extreme stage (ADX < level).",
            id="-extreme-not-reached",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_EXTREME_TREND_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=FIFTY_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=None),
            ),
            False,
            "No ADX value provided.",
            id="-no-adx",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_EXTREME_TREND_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=ZERO_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=FIFTY_PERCENT),
            ),
            False,
            "Level is invalid for consolidation stage (< 25).",
            id="-too-low-level",
        ),
        pytest.param(
            AlgorithmConfigEntity(
                id=TEST_ENTITY_ID,
                title=TEST_ALGORITHM_CONFIG_TITLE,
                algorithm=AlgorithmEnum.ADX_EXTREME_TREND_REACHED,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                level=TWO_HUNDRED_PERCENT,
            ),
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(ADX=FIFTY_PERCENT),
            ),
            False,
            "Level is invalid for consolidation stage (> 100).",
            id="-too-low-level",
        ),
    ),
)
@pytest.mark.unit
def test_adx_extreme_trend_reached(
    algorithm_config: AlgorithmConfigEntity,
    snapshot: MarketDataSnapshotVO,
    expected_result: bool,
    test_description: str,
) -> None:
    logging.log(
        level=logging.INFO,
        msg=test_description,
    )

    result: bool = adx_extreme_trend_reached(
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
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX+DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            True,
            "ADX +DI is growing.",
            id="-pos-di-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": TWENTY_FIVE_PERCENT,
                        "ADX+DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI is declining.",
            id="-pos-di-not-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": None,
                        "ADX+DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI value is missing.",
            id="-pos-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX+DI[1]": None,
                    },
                ),
            ),
            False,
            "ADX +DI previous value is missing.",
            id="-pos-di-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_adx_pos_di_growth(
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
        algorithm=AlgorithmEnum.ADX_POS_DI_GROWTH,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_pos_di_growth(
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
                        "ADX+DI": TWENTY_FIVE_PERCENT,
                        "ADX+DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            True,
            "ADX +DI is declining.",
            id="-pos-di-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX+DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI is growing.",
            id="-pos-di-not-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": None,
                        "ADX+DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI value is missing.",
            id="-pos-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": TWENTY_FIVE_PERCENT,
                        "ADX+DI[1]": None,
                    },
                ),
            ),
            False,
            "ADX +DI previous value is missing.",
            id="-pos-di-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_adx_pos_di_decline(
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
        algorithm=AlgorithmEnum.ADX_POS_DI_DECLINE,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_pos_di_decline(
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
                        "ADX-DI": FIFTY_PERCENT,
                        "ADX-DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            True,
            "ADX -DI is growing.",
            id="-neg-di-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                        "ADX-DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "ADX -DI is declining.",
            id="-neg-di-not-growing",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": None,
                        "ADX-DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX -DI value is missing.",
            id="-neg-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": FIFTY_PERCENT,
                        "ADX-DI[1]": None,
                    },
                ),
            ),
            False,
            "ADX -DI previous value is missing.",
            id="-neg-di-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_adx_neg_di_growth(
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
        algorithm=AlgorithmEnum.ADX_NEG_DI_GROWTH,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_neg_di_growth(
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
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                        "ADX-DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            True,
            "ADX -DI is declining.",
            id="-neg-di-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": FIFTY_PERCENT,
                        "ADX-DI[1]": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX -DI is growing.",
            id="-neg-di-not-declining",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": None,
                        "ADX-DI[1]": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "ADX -DI value is missing.",
            id="-neg-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                        "ADX-DI[1]": None,
                    },
                ),
            ),
            False,
            "ADX -DI previous value is missing.",
            id="-neg-di-missing-previous",
        ),
    ),
)
@pytest.mark.unit
def test_adx_neg_di_decline(
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
        algorithm=AlgorithmEnum.ADX_NEG_DI_DECLINE,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_neg_di_decline(
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
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            True,
            "Bullish crossover (+DI > -DI).",
            id="-bullish-crossover",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": TWENTY_FIVE_PERCENT,
                        "ADX-DI": FIFTY_PERCENT,
                    },
                ),
            ),
            False,
            "No bullish crossover (+DI < -DI).",
            id="-no-bullish-crossover",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": None,
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI value is missing.",
            id="-pos-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX-DI": None,
                    },
                ),
            ),
            False,
            "ADX -DI value is missing.",
            id="-neg-di-missing-current",
        ),
    ),
)
@pytest.mark.unit
def test_adx_di_bullish_crossover(
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
        algorithm=AlgorithmEnum.ADX_DI_BULLISH_CROSSOVER,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_di_bullish_crossover(
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
                        "ADX+DI": TWENTY_FIVE_PERCENT,
                        "ADX-DI": FIFTY_PERCENT,
                    },
                ),
            ),
            True,
            "Bearish crossover (-DI > +DI).",
            id="-bearish-crossover",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "No bearish crossover (-DI < +DI).",
            id="-no-bullish-crossover",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": None,
                        "ADX-DI": TWENTY_FIVE_PERCENT,
                    },
                ),
            ),
            False,
            "ADX +DI value is missing.",
            id="-pos-di-missing-current",
        ),
        pytest.param(
            MarketDataSnapshotVO(
                ticker_id=TEST_ENTITY_ID,
                timeframe=TimeframeEnum.INTERVAL_1_WEEK,
                indicators=IndicatorsSnapshotVO(
                    **{
                        "ADX+DI": FIFTY_PERCENT,
                        "ADX-DI": None,
                    },
                ),
            ),
            False,
            "ADX -DI value is missing.",
            id="-neg-di-missing-current",
        ),
    ),
)
@pytest.mark.unit
def test_adx_di_bearish_crossover(
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
        algorithm=AlgorithmEnum.ADX_DI_BULLISH_CROSSOVER,
        timeframe=TimeframeEnum.INTERVAL_1_WEEK,
        level=ZERO_STUB,
    )
    result = adx_di_bearish_crossover(
        algorithm_config=dummy_config,
        snapshot=snapshot,
    )

    assert result == expected_result
