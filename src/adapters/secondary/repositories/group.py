from collections import defaultdict
from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Engine, Result, select

from src.core.application.exceptions.repositories import FailedToGetGroupsException
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.entities.group import GroupEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.group import GroupRepositoryPort
from src.infrastructure.database.engine import engine
from src.infrastructure.database.models.group import GroupAlgorithmConfigModel, GroupModel


class GroupRepository(GroupRepositoryPort):
    """
    SQLAlchemy Core implementation of GroupRepositoryPort.

    Creates a new connection from the engine in each method
    and loads algorithm config IDs via a separate query.
    """

    def __init__(self, engine: Engine = engine):
        self._engine = engine

    @exc_translator(reraise=FailedToGetGroupsException)
    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[GroupEntity]:
        """
        Returns active groups whose IDs appear in ids.

        Filters rows by is_active=True,
        then loads algorithm config associations
        in a second query.

        :param ids: Group IDs to filter by.

        :return: Active groups matching the given IDs.
        """

        stdlib_ids = [UUID(str(group_id)) for group_id in ids]
        group_stmt = select(
            GroupModel.id,
            GroupModel.title,
            GroupModel.description,
            GroupModel.is_active,
        ).where(
            GroupModel.is_active.is_(True),
            GroupModel.id.in_(stdlib_ids),
        )

        with self._engine.connect() as connection:
            group_result: Result = connection.execute(group_stmt)
            group_rows = group_result.mappings().fetchall()

            if not group_rows:
                return []

            group_ids = [row["id"] for row in group_rows]
            assoc_stmt = select(
                GroupAlgorithmConfigModel.group_id,
                GroupAlgorithmConfigModel.algorithm_config_id,
            ).where(GroupAlgorithmConfigModel.group_id.in_(group_ids))

            assoc_result: Result = connection.execute(assoc_stmt)
            assoc_rows = assoc_result.mappings().fetchall()

        map_of_groups_and_algo_configs: defaultdict = defaultdict(list[UUID])
        for assoc_row in assoc_rows:
            map_of_groups_and_algo_configs[assoc_row["group_id"]].append(assoc_row["algorithm_config_id"])

        groups = [
            GroupEntity.model_validate(
                {
                    **row,
                    "algorithm_config_ids": map_of_groups_and_algo_configs[row["id"]],
                }
            )
            for row in group_rows
        ]

        return groups
