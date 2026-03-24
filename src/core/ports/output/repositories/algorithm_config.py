from abc import ABC, abstractmethod
from collections.abc import Collection

from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.utils.custom_uuid import CustomUUID


class AlgorithmConfigRepositoryPort(ABC):
    """
    Port for retrieving configurations of algorithms
    for signal calculation.
    """

    @abstractmethod
    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[AlgorithmConfigEntity]: ...
