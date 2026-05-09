from src.core.domain.entities.base import BaseEntityWithID
from src.core.domain.utils.custom_uuid import CustomUUID


class SignalCalculationConfigEntity(BaseEntityWithID):
    """
    Local entity of signal calculation configuration for ticker.
    Links group of algorithm configurations and signal expiration time.
    """

    group_id: CustomUUID
    signal_expiration_timestamp: float
    is_active: bool = True
