from collections import defaultdict

from sqlalchemy import Engine, Result, select
from sqlalchemy.engine import RowMapping

from src.core.application.exceptions.repositories import FailedToGetTickersException
from src.core.application.utils.exception_translator import exc_translator
from src.core.domain.entities.signal_calculation_config import SignalCalculationConfigEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.value_objects.master_data.exchange import ExchangeVO
from src.core.ports.output.repositories.ticker import TickerRepositoryPort
from src.infrastructure.database.engine import engine
from src.infrastructure.database.models.exchange import ExchangeModel
from src.infrastructure.database.models.signal_calculation_config import SignalCalculationConfigModel
from src.infrastructure.database.models.ticker import TickerModel


class TickerRepository(TickerRepositoryPort):
    """
    SQLAlchemy Core implementation of TickerRepositoryPort.

    Creates a new connection from the engine in each method
    and maps active tickers to TickerEntity objects.
    """

    def __init__(self, engine: Engine = engine):
        self._engine = engine

    @exc_translator(reraise=FailedToGetTickersException)
    def get_all_active(self) -> list[TickerEntity]:
        """
        Returns all tickers where is_active is True.

        Fetches tickers joined with exchanges,
        then loads active calculation configs in a second query.

        :return: Active tickers with exchange
        and calculation configs attached.
        """

        ticker_stmt = (
            select(
                TickerModel.id,
                TickerModel.title,
                TickerModel.key,
                TickerModel.screener,
                TickerModel.is_active,
                ExchangeModel.title.label("exchange_title"),
                ExchangeModel.key.label("exchange_key"),
            )
            .join(
                ExchangeModel,
                TickerModel.exchange_id == ExchangeModel.id,
            )
            .where(TickerModel.is_active.is_(True))
        )

        calc_config_stmt = select(
            SignalCalculationConfigModel.id,
            SignalCalculationConfigModel.ticker_id,
            SignalCalculationConfigModel.group_id,
            SignalCalculationConfigModel.signal_expiration_timestamp,
            SignalCalculationConfigModel.is_active,
        ).where(
            SignalCalculationConfigModel.is_active.is_(True),
            SignalCalculationConfigModel.ticker_id.in_(
                select(TickerModel.id).where(TickerModel.is_active.is_(True)),
            ),
        )

        with self._engine.connect() as connection:
            ticker_result: Result = connection.execute(ticker_stmt)
            ticker_rows = ticker_result.mappings().fetchall()

            if not ticker_rows:
                return []

            calc_config_result: Result = connection.execute(calc_config_stmt)
            calc_config_rows = calc_config_result.mappings().fetchall()

        map_of_tickers_and_calc_configs: defaultdict = defaultdict(list[RowMapping])
        for calc_config_row in calc_config_rows:
            map_of_tickers_and_calc_configs[calc_config_row["ticker_id"]].append(calc_config_row)

        tickers = [
            self._to_entity(
                ticker_row=ticker_row,
                calc_config_rows=map_of_tickers_and_calc_configs[ticker_row["id"]],
            )
            for ticker_row in ticker_rows
        ]

        return tickers

    def _to_entity(
        self,
        ticker_row: RowMapping,
        calc_config_rows: list[RowMapping],
    ) -> TickerEntity:
        """
        Maps a ticker query row and its calc config rows
        to a TickerEntity.

        Builds ExchangeVO from the flat exchange columns,
        then delegates remaining field mapping to model_validate.

        :param ticker_row: Row from the tickers-exchanges join.
        :param calc_config_rows: Calculation config rows
        for this ticker.

        :return: TickerEntity assembled from the provided rows.
        """

        ticker_dict = dict(ticker_row)

        exchange = ExchangeVO(
            title=ticker_dict.pop("exchange_title"),
            key=ticker_dict.pop("exchange_key"),
        )
        calculation_configs = [
            SignalCalculationConfigEntity.model_validate(calc_config_row) for calc_config_row in calc_config_rows
        ]
        ticker = TickerEntity.model_validate(
            {
                **ticker_dict,
                "exchange": exchange,
                "calculation_configs": calculation_configs,
            },
        )

        return ticker
