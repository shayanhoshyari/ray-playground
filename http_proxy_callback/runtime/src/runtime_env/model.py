import logging

import fastapi
import fastapi.encoders
import pydantic
import ray.serve
from runtime_env.pydev import PydevConfig, connect_to_pydev

logger = logging.getLogger("ray.serve")

app = fastapi.FastAPI()


class Body(pydantic.BaseModel):
    message: str


class Response(pydantic.BaseModel):
    message: str
    affirmative: str


@ray.serve.deployment(route_prefix="/")
@ray.serve.ingress(app)
class Model:
    def __init__(self, pydev_config: PydevConfig | None = None) -> None:
        if pydev_config is not None:
            # If the pydev_config is provided, connect to it.
            connect_to_pydev(pydev_config)

    @app.put(
        "/put",
        response_model=Response,
    )
    async def root(
        self, request: fastapi.Request, body: Body = fastapi.Body()
    ) -> Response:
        logger.debug("Received request - processing")
        logger.info("x-request-id: %s", request.headers.get("x-request-id"))
        return Response(affirmative=True, message=body.message)
