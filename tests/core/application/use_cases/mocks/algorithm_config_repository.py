from collections.abc import Collection

from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.algorithm_config import AlgorithmConfigRepositoryPort


class InMemoryAlgorithmConfigRepository(AlgorithmConfigRepositoryPort):
    """
    In memory repository for retrieving configurations of algorithms
    for signal calculation.
    """

    def __init__(
        self,
        algorithm_configs: list[AlgorithmConfigEntity] | None = None,
    ):
        self._algorithm_configs = algorithm_configs or []

    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[AlgorithmConfigEntity]:
        unique_ids = set(ids)
        filtered_algorithm_configs = [
            algorithm_config
            for algorithm_config in self._algorithm_configs
            if algorithm_config.is_active and algorithm_config.id in unique_ids
        ]

        return filtered_algorithm_configs
