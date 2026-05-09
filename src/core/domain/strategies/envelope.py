from typing import TYPE_CHECKING

from src.core.domain.constants.boundaries import UNIT_SHARE, ZERO_SHARE

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


def envelope_lower_boundary_breakout(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if current price is breaking lower envelope boundary.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if algorithm_config.moving_average is None or snapshot.close is None:
        return False

    if not (ZERO_SHARE <= algorithm_config.level <= UNIT_SHARE):
        return False

    ma_current_value: float | None = getattr(snapshot.indicators, algorithm_config.moving_average.value, None)
    if ma_current_value is None:
        return False

    current_price: float = snapshot.close

    result = current_price <= ma_current_value * algorithm_config.level

    return result


def envelope_upper_boundary_breakout(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if current price is breaking upper envelope boundary.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if algorithm_config.moving_average is None or snapshot.close is None:
        return False

    if algorithm_config.level < UNIT_SHARE:
        return False

    ma_current_value: float | None = getattr(snapshot.indicators, algorithm_config.moving_average.value, None)
    if ma_current_value is None:
        return False

    current_price: float = snapshot.close

    result = current_price >= ma_current_value * algorithm_config.level

    return result
