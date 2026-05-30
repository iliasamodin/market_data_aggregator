from collections.abc import Callable

from robyn import Request, Response, SubRouter
from robyn import status_codes

from src.adapters.primary.http.auth import api_key_auth_handler
from src.adapters.primary.utils.response_preparer import prepare_response_detail
from src.core.application.dtos.signal_evaluator import SignalEvaluationResultDTO
from src.core.application.exceptions.signal_evaluator import (
    AlgorithmConfigsMissingException,
    BaseSignalEvaluatorException,
    GroupsMissingException,
    TickersMissingException,
)
from src.core.ports.input.signal_evaluator import SignalEvaluatorInputPort


def create_signal_evaluator_router(
    signal_evaluator_factory: Callable[[], SignalEvaluatorInputPort],
    prefix: str = "",
) -> SubRouter:
    """
    Build and return a SubRouter for the signal evaluator endpoint.

    Accepts a factory callable instead of a use case instance
    so that each request gets a fresh SignalEvaluatorUseCase
    with a clean SignalEvaluationResultDTO.
    The factory is captured via closure,
    keeping the adapter free of any bootstrap imports.

    :param signal_evaluator_factory: Zero-argument callable
    that returns a ready SignalEvaluatorInputPort instance.
    :param prefix: URL prefix to prepend to all routes
    in this router (e.g. the global API prefix).

    :return: Configured SubRouter with the execute endpoint registered.
    """

    tag = "signal-evaluator"

    router = SubRouter(__file__, prefix=f"{prefix}/{tag}")
    router.configure_authentication(api_key_auth_handler)

    @router.post(
        "/v1/execute",
        auth_required=True,
        openapi_tags=[tag],
    )
    def execute_signal_evaluation(_request: Request) -> Response:
        """
        Trigger a full cycle of trading signal evaluation.

        Runs the evaluation cycle for all active tickers
        and returns execution statistics.

        :return: 200 with SignalEvaluationResultDTO on success,
        401 if the Authorization header is absent or the key is invalid,
        503 if required master data is missing in the database,
        500 on unexpected error.
        """

        headers = {
            "Content-Type": "application/json",
        }
        try:
            use_case = signal_evaluator_factory()
            result: SignalEvaluationResultDTO = use_case.execute()

            return Response(
                status_code=status_codes.HTTP_200_OK,
                headers=headers,
                description=result.model_dump_json(),
            )

        except (
            TickersMissingException,
            GroupsMissingException,
            AlgorithmConfigsMissingException,
        ) as exc:
            return Response(
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE,
                headers=headers,
                description=prepare_response_detail(exc.detail),
            )

        except BaseSignalEvaluatorException as exc:
            return Response(
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
                headers=headers,
                description=prepare_response_detail(exc.detail),
            )

        except Exception:
            return Response(
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
                headers=headers,
                description=prepare_response_detail(),
            )

    return router
