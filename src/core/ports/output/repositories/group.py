from abc import ABC, abstractmethod
from collections.abc import Collection

from src.core.domain.entities.group import GroupEntity
from src.core.domain.utils.custom_uuid import CustomUUID


class GroupRepositoryPort(ABC):
    """
    Port for retrieving groups of algorithm configurations.
    """

    @abstractmethod
    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[GroupEntity]: ...
