"""
Test with

* Launch `RAY: Test Server`

* Run python fastapi-disconnect/request.py

  * If you don't press ctrl+c, you will see this printed:
      INFO - Request still good, sleeping
      INFO - 127.0.0.1:35230 - "PUT / HTTP/1.1" 200

  * If you press Ctrl+c
     The behaviour is not consistent with uvicorn, you still see the same behavior
     as not pressing ctrl.
"""

import asyncio
import contextlib
import logging
from typing import AsyncIterator

import fastapi
import fastapi.encoders
import pydantic
import ray.serve

logger = logging.getLogger("ray.serve")

SLEEP_PERIOD = 0.2

app = fastapi.FastAPI()


def raise_if_failed(task: asyncio.Task[object | None]) -> None:
    if task.cancelled():
        return

    if not task.done():
        return

    exc = task.exception()
    if exc is not None:
        raise exc


class Body(pydantic.BaseModel):
    message: str


class Response(pydantic.BaseModel):
    affirmative: str


@contextlib.asynccontextmanager
async def observe_http_request(request: fastapi.Request) -> AsyncIterator[None]:
    """
    Observes a fastapi (starlette) task, will call task manager's cancel if the
    user drops the http API request.
    """

    async def observe_loop() -> None:
        while True:
            if await request.is_disconnected():
                logger.info("Request dropped")
                return
            else:
                logger.info("Request %s still good, sleeping", await request.json())
            await asyncio.sleep(SLEEP_PERIOD)

    observe_task = asyncio.create_task(observe_loop())
    try:
        yield None
    finally:
        # Kill the observe loop
        raise_if_failed(observe_task)
        observe_task.cancel()


@ray.serve.deployment(route_prefix="/")
@ray.serve.ingress(app)
class FastAPIDeployment:
    @app.put(
        "/put",
        response_model=Response,
    )
    async def root(self, request: fastapi.Request, body: Body = fastapi.Body()) -> fastapi.Response:
        logger.debug("Received request - processing")
        async with observe_http_request(request):
            await asyncio.sleep(4)
            result = fastapi.encoders.jsonable_encoder(Response(affirmative=body.message))
            return fastapi.responses.JSONResponse(content=result)

deploy = FastAPIDeployment.bind() # type: ignore

if __name__ == "__main__":
    import time
    ray.init()
    ray.serve.start(detached=True)
    ray.serve.run(deploy)
    try:
        while True:
            # Block, letting Ray print logs to the terminal
            time.sleep(10)
    finally:
        logger.info("Shutting down ray.")
        ray.shutdown()
