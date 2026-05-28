from dependency_injector import containers, providers

from src.adapters.secondary.providers.market_data import TradingViewMarketDataProvider
from src.adapters.secondary.providers.notification import TelegramNotificationProvider
from src.adapters.secondary.repositories.algorithm_config import AlgorithmConfigRepository
from src.adapters.secondary.repositories.group import GroupRepository
from src.adapters.secondary.repositories.signal_history import SignalHistoryRepository
from src.adapters.secondary.repositories.ticker import TickerRepository
from src.core.application.use_cases.signal_evaluator import SignalEvaluatorUseCase
from src.infrastructure.database.engine import engine as db_engine


class SignalEvaluatorContainer(containers.DeclarativeContainer):
    """
    DI container for SignalEvaluatorUseCase.

    The engine is an explicit provider so it can be overridden
    from outside the container (e.g. a test engine in tests).
    Repositories are singletons within a container instance —
    they are stateless beyond the injected engine.
    The use case is a factory
    so that each call produces a fresh instance
    with a clean SignalEvaluationResultDTO.
    """

    engine = providers.Object(db_engine)

    ticker_repo = providers.Singleton(
        TickerRepository,
        engine=engine,
    )
    group_repo = providers.Singleton(
        GroupRepository,
        engine=engine,
    )
    algorithm_repo = providers.Singleton(
        AlgorithmConfigRepository,
        engine=engine,
    )
    signal_history_repo = providers.Singleton(
        SignalHistoryRepository,
        engine=engine,
    )

    market_data_provider = providers.Singleton(TradingViewMarketDataProvider)
    notification_provider = providers.Singleton(TelegramNotificationProvider)

    signal_evaluator = providers.Factory(
        SignalEvaluatorUseCase,
        ticker_repo=ticker_repo,
        group_repo=group_repo,
        algorithm_repo=algorithm_repo,
        signal_history_repo=signal_history_repo,
        market_data_provider=market_data_provider,
        notification_provider=notification_provider,
    )


signal_evaluator_container = SignalEvaluatorContainer()
