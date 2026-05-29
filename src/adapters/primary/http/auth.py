from robyn import Response, status_codes
from robyn.authentication import AuthenticationHandler, BearerGetter
from robyn.robyn import Identity, Request

from src.adapters.primary.constants.shared import UnsuccessfulResponseDetailEnum
from src.adapters.primary.http.configs import http_server_configs
from src.adapters.primary.utils.response_preparer import prepare_response_detail


class ApiKeyAuthenticationHandler(AuthenticationHandler):
    """
    Bearer API-key authentication handler for Robyn.

    Extracts the token from the Authorization header via BearerGetter
    and compares it against the configured API key.
    Returns an Identity on success and None on failure;
    Robyn sends <unauthorized_response> automatically
    when None is returned.
    """

    def __init__(self):
        bearer_getter = BearerGetter()
        super().__init__(token_getter=bearer_getter)

    @property
    def unauthorized_response(self) -> Response:
        return Response(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            headers={
                "Content-Type": "application/json",
            },
            description=prepare_response_detail(UnsuccessfulResponseDetailEnum.MISSING_OR_INVALID_AUTH_HEADER),
        )

    def authenticate(self, request: Request) -> Identity | None:
        """
        Validate the Bearer token against the configured API key.

        :param request: Incoming HTTP request.

        :return: Identity with empty claims on success, None on failure.
        """

        token = self.token_getter.get_token(request)
        if token != http_server_configs.API_AUTH_KEY:
            return None

        identity = Identity(claims={})

        return identity


api_key_auth_handler = ApiKeyAuthenticationHandler()
