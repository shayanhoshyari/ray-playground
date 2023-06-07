import functools
import logging
import os
import re
import typing

from runtime_env.pydev import PYDEV_CONFIG_KEY, PydevConfig, connect_to_pydev
from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("ray.serve")


class RequestIDMiddleware:
    #ADAPTED FROM: https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.simple_response(scope, receive, send)

    async def simple_response(
        self, scope: Scope, receive: Receive, send: Send, request_headers: Headers
    ) -> None:
        send = functools.partial(self.send, send=send)
        await self.app(scope, receive, send)

    async def send(
        self, message: Message, send: Send
    ) -> None:
        if message["type"] != "http.response.start":
            await send(message)
            return

        message.setdefault("headers", [])
        headers = MutableHeaders(scope=message)
        headers.update({"x-request-id": "goooooz"})

        await send(message)


def proxy_callback() -> list[Middleware]:
    pydev_config = os.getenv(PYDEV_CONFIG_KEY)
    if pydev_config is not None:
        connect_to_pydev(PydevConfig.parse_raw(pydev_config))
    return [Middleware(RequestIDMiddleware)]
