import json

from robyn import Robyn
from robyn.openapi import Components, OpenAPI, OpenAPIInfo

from src.bootstrap.agg_router import aggregating_router
from src.bootstrap.constants.openapi import OPENAPI_SPEC_PATH
from src.bootstrap.exceptions.lifespan import FailedToCloseEngineConnectsToDBException
from src.infrastructure.database.engine import engine

__version__ = "0.2.0"

app = Robyn(
    file_object=__file__,
    openapi=OpenAPI(
        info=OpenAPIInfo(
            title="Market data aggregator",
            description=(
                "Market data collection and aggregation service. "
                "It implements positional trading strategies "
                "and notifies the trader about potential market entry points."
            ),
            version=__version__,
            components=Components(
                securitySchemes={
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                    },
                },
            ),
        )
    ),
)

# Include main router
app.include_router(router=aggregating_router)

# Load the pre-generated spec with security if it exists.
# openapi_file_override=True prevents prepare_routes_openapi
# from overwriting the spec with the auto-generated version
if OPENAPI_SPEC_PATH.exists() and app.openapi is not None:
    app.openapi.openapi_spec = json.loads(OPENAPI_SPEC_PATH.read_text())
    app.openapi.openapi_file_override = True


@app.shutdown_handler
def shutdown_event():
    """
    Shutdown event handler.

    Closes the database engine connection pool.
    """

    try:
        engine.dispose()

    except Exception:
        raise FailedToCloseEngineConnectsToDBException()
