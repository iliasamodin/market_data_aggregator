from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Engine, Result, exists, insert, select, update

from src.core.application.exceptions.repositories import (
    FailedToCheckRecentSignalException,
    FailedToSaveSignalException,
)
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.signal_history import HistoricalSignalEntity
from src.core.domain.utils.custom_uuid import CustomUUID
from src.core.ports.output.repositories.signal_history import SignalHistoryRepositoryPort
from src.infrastructure.database.engine import engine
from src.infrastructure.database.models.signal_history import HistoricalSignalModel


class SignalHistoryRepository(SignalHistoryRepositoryPort):
    """
    SQLAlchemy Core implementation of SignalHistoryRepositoryPort.

    Creates a new connection from the engine in each method
    to check for recent signals and persist new ones.
    """

    def __init__(self, engine: Engine = engine):
        self._engine = engine

    @exc_translator(reraise=FailedToCheckRecentSignalException)
    def has_recent_signal(
        self,
        calculation_config_id: CustomUUID,
        delta: timedelta,
        status: SignalStatusEnum,
    ) -> bool:
        """
        Returns True if a recent signal matching the criteria exists.

        Checks for a signal_history row
        where calculation_config_id, status, and create_dt
        (within the last delta period) all match.

        :param calculation_config_id: Calculation config ID.
        :param delta: Lookback window;
        signals within now minus delta are considered recent.
        :param status: Signal status to match.

        :return: True if a matching recent signal exists.
        """

        stdlib_config_id = UUID(str(calculation_config_id))
        min_actual_dt = datetime.now(tz=UTC) - delta
        stmt = select(
            exists().where(
                HistoricalSignalModel.calculation_config_id == stdlib_config_id,
                HistoricalSignalModel.status == status,
                HistoricalSignalModel.create_dt >= min_actual_dt,
            )
        )

        with self._engine.connect() as connection:
            stmt_result: Result = connection.execute(stmt)
            result = bool(stmt_result.scalar())

        return result

    @exc_translator(reraise=FailedToSaveSignalException)
    def save(self, signal: HistoricalSignalEntity) -> None:
        """
        Persists a HistoricalSignalEntity to signal_history.

        If a row with the same ID already exists,
        updates its status field only.
        Otherwise inserts a new row with all fields.

        :param signal: Signal entity to persist.
        """

        stdlib_signal_id = UUID(str(signal.id))
        if self._has_signal(signal.id):
            stmt = (
                update(HistoricalSignalModel)
                .values(status=signal.status)
                .where(HistoricalSignalModel.id == stdlib_signal_id)
            )

        else:
            stdlib_config_id = UUID(str(signal.calculation_config_id))
            stmt = insert(HistoricalSignalModel).values(
                id=stdlib_signal_id,
                calculation_config_id=stdlib_config_id,
                create_dt=signal.create_dt,
                status=signal.status,
            )

        with self._engine.begin() as connection:
            connection.execute(stmt)

    def _has_signal(self, signal_id: CustomUUID) -> bool:
        """
        Check if a signal with the given ID exists.

        :param signal_id: Signal ID to check.

        :return: True if a signal with the given ID exists.
        """

        stdlib_signal_id = UUID(str(signal_id))
        stmt = select(
            exists().where(HistoricalSignalModel.id == stdlib_signal_id),
        )

        with self._engine.connect() as connection:
            stmt_result: Result = connection.execute(stmt)
            result = bool(stmt_result.scalar())

        return result
