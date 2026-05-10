from collections.abc import Collection

from src.core.domain.entities.group import GroupEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.group import GroupRepositoryPort


class InMemoryGroupRepository(GroupRepositoryPort):
    """
    In memory repository
    for retrieving groups of algorithm configurations.
    """

    def __init__(self, groups: list[GroupEntity] | None = None):
        self._groups = groups or []

    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[GroupEntity]:
        unique_ids = set(ids)
        filtered_groups = [group for group in self._groups if group.id in unique_ids and group.is_active]

        return filtered_groups
