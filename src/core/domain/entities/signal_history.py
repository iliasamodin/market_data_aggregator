from datetime import UTC, datetime

from pydantic import Field

from src.core.domain.constants.signal_status import SignalStatusEnum
from src.core.domain.entities.base import BaseEntityWithID
from src.core.domain.utils.custom_uuid import CustomUUID


class HistoricalSignalEntity(BaseEntityWithID):
    """
    Entity of historical trading signal.
    """

    calculation_config_id: CustomUUID
    create_dt: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    status: SignalStatusEnum = SignalStatusEnum.CREATED
