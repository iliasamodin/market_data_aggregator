from src.core.domain.entities.ticker import TickerEntity
from src.core.ports.output.repositories.ticker import TickerRepositoryPort


class InMemoryTickerRepository(TickerRepositoryPort):
    """
    In memory repository for retrieving tickers
    with their signal calculation configurations.
    """

    def __init__(self, tickers: list[TickerEntity] | None = None):
        self._tickers = tickers or []

    def get_all_active(self) -> list[TickerEntity]:
        active_tickers = [ticker for ticker in self._tickers if ticker.is_active]

        return active_tickers
