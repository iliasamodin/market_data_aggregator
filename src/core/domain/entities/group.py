from collections.abc import Collection, Mapping
from typing import TYPE_CHECKING

from pydantic import Field

from src.core.domain.constants.timeframe import TimeframeEnum
from src.core.domain.entities.base import BaseEntityWithIDAndTitle
from src.core.domain.utils.custom_uuid import CustomUUID

if TYPE_CHECKING:
    from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
    from src.core.domain.value_objects.operational_data.market_data import MarketDataSnapshotVO


class GroupEntity(BaseEntityWithIDAndTitle):
    """
    Entity to group of algorithm configurations
    joined by the AND operator.
    """

    description: str
    is_active: bool = True

    algorithm_config_ids: list[CustomUUID] = Field(default_factory=list)

    def is_triggered(
        self,
        algorithm_configs: Collection["AlgorithmConfigEntity"],
        map_of_snapshots: Mapping[TimeframeEnum, "MarketDataSnapshotVO"],
    ) -> bool:
        """
        Check if conditions of strategies is met
        for configurations of algorithms.

        :param algorithm_configs: Configurations of algorithms.
        :param map_of_snapshots: Map of timeframes and snapshots.

        :return: Result of strategies for configurations of algorithms.
        """

        if not self.is_active or not algorithm_configs:
            return False

        group_algorithm_configs = tuple(
            algorithm_config
            for algorithm_config in algorithm_configs
            if algorithm_config.id in self.algorithm_config_ids
        )

        if not group_algorithm_configs:
            return False

        for algorithm_config in group_algorithm_configs:
            snapshot = map_of_snapshots.get(algorithm_config.timeframe)

            if not snapshot:
                return False

            if not algorithm_config.is_triggered(snapshot):
                return False

        return True
