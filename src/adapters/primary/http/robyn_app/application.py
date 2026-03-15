from robyn import Robyn
from robyn.openapi import OpenAPI, OpenAPIInfo

__version__ = "0.1.0"

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
        )
    ),
)


@app.startup_handler
def startup_event():
    """
    Startup event handler.
    """


@app.shutdown_handler
def shutdown_event():
    """
    Shutdown event handler.
    """
