from pydantic import Field

from src.core.domain.constants.screener import ScreenerEnum
from src.core.domain.entities.base import BaseEntityWithIDAndTitle
from src.core.domain.value_objects.master_data.exchange import ExchangeVO
from src.core.domain.entities.signal_calculation_config import SignalCalculationConfigEntity


class TickerEntity(BaseEntityWithIDAndTitle):
    """
    Entity of trading ticker.
    """

    key: str
    screener: ScreenerEnum
    is_active: bool = True

    exchange: ExchangeVO

    calculation_configs: list[SignalCalculationConfigEntity] = Field(default_factory=list)
