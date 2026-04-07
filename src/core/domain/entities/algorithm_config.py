from typing import TYPE_CHECKING

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.constants.moving_average import MovingAverageEnum
from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.base import BaseEntityWithIDAndTitle
from src.core.domain.types import StrategyType

if TYPE_CHECKING:
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


class AlgorithmConfigEntity(BaseEntityWithIDAndTitle):
    """
    Entity to configuration of algorithm.
    """

    algorithm: AlgorithmEnum
    timeframe: TimeframeEnum
    level: float
    moving_average: MovingAverageEnum | None = None
    description: str | None = None
    is_active: bool = True

    def is_triggered(self, snapshot: "MarketDataSnapshotVO") -> bool:
        """
        Check if the strategy condition is met
        for the algorithm configuration.

        :param snapshot: Current market data.

        :return: Strategy result for the algorithm configuration.
        """

        if not self.is_active:
            return False

        from src.core.domain.strategies import STRATEGY_MAP

        strategy_func: StrategyType | None = STRATEGY_MAP.get(self.algorithm)
        if not strategy_func:
            raise ValueError(f"Strategy for {self.algorithm} is not registered.")

        result = strategy_func(self, snapshot)

        return result
