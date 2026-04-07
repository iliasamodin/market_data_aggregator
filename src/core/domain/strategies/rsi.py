from typing import TYPE_CHECKING

from src.core.domain.constants.boundaries import FIFTY_PERCENT, ONE_HUNDRED_PERCENT, ZERO_PERCENT

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


def rsi_oversold_reached(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that RSI has reached the oversold level.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.rsi is None:
        return False

    if not (ZERO_PERCENT <= algorithm_config.level <= FIFTY_PERCENT):
        return False

    result = snapshot.indicators.rsi <= algorithm_config.level

    return result


def rsi_overbought_reached(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that RSI has reached the overbought level.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.rsi is None:
        return False

    if not (FIFTY_PERCENT <= algorithm_config.level <= ONE_HUNDRED_PERCENT):
        return False

    result = snapshot.indicators.rsi >= algorithm_config.level

    return result


def rsi_growth(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the RSI direction is bullish based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.rsi is None or snapshot.indicators.previous_rsi is None:
        return False

    result = snapshot.indicators.rsi > snapshot.indicators.previous_rsi

    return result


def rsi_decline(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check that the RSI direction is bearish based on the last two bars.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.rsi is None or snapshot.indicators.previous_rsi is None:
        return False

    result = snapshot.indicators.rsi < snapshot.indicators.previous_rsi

    return result
