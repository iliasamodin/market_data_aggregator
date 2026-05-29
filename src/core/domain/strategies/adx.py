from typing import TYPE_CHECKING

from src.core.domain.constants.boundaries import ONE_HUNDRED_PERCENT, TWENTY_FIVE_PERCENT, ZERO_PERCENT

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


def adx_consolidation_stage_transition(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the trend has entered the consolidation stage
    based on ADX.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx is None:
        return False

    if not (ZERO_PERCENT <= algorithm_config.level <= TWENTY_FIVE_PERCENT):
        return False

    result = snapshot.indicators.adx <= algorithm_config.level

    return result


def adx_extreme_trend_reached(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the trend has entered the extreme stage based on ADX.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx is None:
        return False

    if not (TWENTY_FIVE_PERCENT <= algorithm_config.level <= ONE_HUNDRED_PERCENT):
        return False

    result = snapshot.indicators.adx >= algorithm_config.level

    return result


def adx_pos_di_growth(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the ADX +DI is growing based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_pos_di is None or snapshot.indicators.previous_adx_pos_di is None:
        return False

    result = snapshot.indicators.adx_pos_di > snapshot.indicators.previous_adx_pos_di

    return result


def adx_pos_di_decline(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the ADX +DI is declining based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_pos_di is None or snapshot.indicators.previous_adx_pos_di is None:
        return False

    result = snapshot.indicators.adx_pos_di < snapshot.indicators.previous_adx_pos_di

    return result


def adx_neg_di_growth(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the ADX -DI is growing based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_neg_di is None or snapshot.indicators.previous_adx_neg_di is None:
        return False

    result = snapshot.indicators.adx_neg_di > snapshot.indicators.previous_adx_neg_di

    return result


def adx_neg_di_decline(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the ADX -DI is declining based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_neg_di is None or snapshot.indicators.previous_adx_neg_di is None:
        return False

    result = snapshot.indicators.adx_neg_di < snapshot.indicators.previous_adx_neg_di

    return result


def adx_di_bullish_crossover(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if there is a bullish crossover of the ADX +DI
    through the ADX -DI (+DI > -DI).

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_pos_di is None or snapshot.indicators.adx_neg_di is None:
        return False

    result = snapshot.indicators.adx_pos_di >= snapshot.indicators.adx_neg_di

    return result


def adx_di_bearish_crossover(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if there is a bearish crossover of the ADX -DI
    through the ADX +DI (-DI > +DI).

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.adx_pos_di is None or snapshot.indicators.adx_neg_di is None:
        return False

    result = snapshot.indicators.adx_neg_di >= snapshot.indicators.adx_pos_di

    return result
