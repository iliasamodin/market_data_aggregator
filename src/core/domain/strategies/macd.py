from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


def macd_signal_line_bullish_crossover(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if there is a bullish crossover of the MACD fast line
    through the signal line.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.macd is None or snapshot.indicators.macd_signal is None:
        return False

    result = snapshot.indicators.macd >= snapshot.indicators.macd_signal

    return result


def macd_signal_line_bearish_crossover(
    algorithm_config: "AlgorithmConfigEntity",
    snapshot: "MarketDataSnapshotVO",
) -> bool:
    """
    Check if there is a bearish crossover of the MACD fast line
    through the signal line.

    :param algorithm_config: Algorithm config.
    :param snapshot: Current market data.

    :return: Strategy result.
    """

    if snapshot.indicators.macd is None or snapshot.indicators.macd_signal is None:
        return False

    result = snapshot.indicators.macd <= snapshot.indicators.macd_signal

    return result
