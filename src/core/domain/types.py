from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

from src.core.domain.constants.algorithm import AlgorithmEnum

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO

StrategyType: TypeAlias = Callable[["AlgorithmConfigEntity", "MarketDataSnapshotVO"], bool]
StrategyMapType: TypeAlias = dict[AlgorithmEnum, StrategyType]
