import asyncio
import contextlib
import logging
from typing import AsyncIterator

import fastapi
import fastapi.encoders
import pydantic

logger = logging.getLogger(__name__)

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


@app.put(
    "/put",
    response_model=Response,
)
async def _(request: fastapi.Request, body: Body = fastapi.Body()) -> fastapi.Response:
    logger.debug("Received request - processing")
    async with observe_http_request(request):
        await asyncio.sleep(4)
        result = fastapi.encoders.jsonable_encoder(Response(affirmative=body.message))
        return fastapi.responses.JSONResponse(content=result)
