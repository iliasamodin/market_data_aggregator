from robyn import SubRouter

from src.adapters.primary.http.endpoints.signal_evaluator import create_signal_evaluator_router
from src.adapters.primary.http.configs import http_server_configs
from src.bootstrap.di.signal_evaluator import signal_evaluator_container

aggregating_router = SubRouter(__file__)

aggregating_router.include_router(
    router=create_signal_evaluator_router(
        signal_evaluator_factory=signal_evaluator_container.signal_evaluator,
        prefix=http_server_configs.API_PREFIX,
    ),
)
