"""
Regenerate src/bootstrap/openapi/openapi.json
with security scheme injected.

Run this script whenever routes change:
    uv run python scripts/generate_openapi.py

Does not require a running server:
generates the spec by calling prepare_routes_openapi
directly on the Robyn router.
The generated file is loaded by Robyn on the next startup
instead of the auto-generated spec,
ensuring the Authorize button appears in Swagger UI.
"""

import json
import logging

from src.bootstrap.constants.openapi import OPENAPI_SPEC_PATH
from src.bootstrap.web import app

if __name__ == "__main__":
    if app.openapi is None:
        raise RuntimeError("OpenAPI is not configured on the app.")

    # Reset the override flag and clear existing paths
    # so that prepare_routes_openapi can regenerate them
    # from registered routes
    app.openapi.openapi_file_override = False
    app.openapi.openapi_spec["paths"] = {}

    app.router.prepare_routes_openapi(
        openapi=app.openapi,
        included_routers=app.included_routers,
    )

    for path_obj in app.openapi.openapi_spec.get("paths", {}).values():
        for operation in path_obj.values():
            if isinstance(operation, dict):
                operation["security"] = [{"BearerAuth": []}]

    OPENAPI_SPEC_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    OPENAPI_SPEC_PATH.write_text(
        data=json.dumps(
            app.openapi.openapi_spec,
            indent=2,
            ensure_ascii=False,
        ),
    )
    logging.log(
        level=logging.INFO,
        msg=f"Saved OpenAPI spec to {OPENAPI_SPEC_PATH}",
    )
