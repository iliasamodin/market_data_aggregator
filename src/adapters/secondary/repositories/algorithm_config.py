from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Engine, Result, select

from src.core.application.exceptions.repositories import FailedToGetAlgorithmConfigsException
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.entities.algorithm_config import AlgorithmConfigEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.algorithm_config import AlgorithmConfigRepositoryPort
from src.infrastructure.database.engine import engine
from src.infrastructure.database.models.algorithm_config import AlgorithmConfigModel


class AlgorithmConfigRepository(AlgorithmConfigRepositoryPort):
    """
    SQLAlchemy Core implementation of AlgorithmConfigRepositoryPort.

    Creates a new connection from the engine in each method
    and maps rows to AlgorithmConfigEntity domain objects.
    """

    def __init__(self, engine: Engine = engine):
        self._engine = engine

    @exc_translator(reraise=FailedToGetAlgorithmConfigsException)
    def get_active_by_ids(self, ids: Collection[CustomUUID]) -> list[AlgorithmConfigEntity]:
        """
        Returns active algorithm configs whose IDs are in ids.

        Filters rows by is_active=True
        and matches against the provided collection
        of algorithm config IDs.

        :param ids: Algorithm config IDs to filter by.

        :return: Active algorithm configs matching the IDs.
        """

        stdlib_ids = [UUID(str(algo_config_id)) for algo_config_id in ids]
        stmt = select(
            AlgorithmConfigModel.id,
            AlgorithmConfigModel.title,
            AlgorithmConfigModel.algorithm,
            AlgorithmConfigModel.timeframe,
            AlgorithmConfigModel.level,
            AlgorithmConfigModel.moving_average,
            AlgorithmConfigModel.description,
            AlgorithmConfigModel.is_active,
        ).where(
            AlgorithmConfigModel.is_active.is_(True),
            AlgorithmConfigModel.id.in_(stdlib_ids),
        )

        with self._engine.connect() as connection:
            stmt_result: Result = connection.execute(stmt)
            rows = stmt_result.mappings().fetchall()

        algorithm_configs = [AlgorithmConfigEntity.model_validate(row) for row in rows]

        return algorithm_configs
