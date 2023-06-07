import logging
import os

from runtime_env.pydev import PYDEV_CONFIG_KEY, PydevConfig, connect_to_pydev
from starlette.middleware import Middleware
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ray.serve")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        headers = dict(request.scope['headers'])
        headers[b'x-request-id'] = b'123'
        request.scope['headers'] = [(k, v) for k, v in headers.items()]

        response = await call_next(request)
        return response


def proxy_callback() -> list[Middleware]:
    pydev_config = os.getenv(PYDEV_CONFIG_KEY)
    if pydev_config is not None:
        connect_to_pydev(PydevConfig.parse_raw(pydev_config))
    return [Middleware(RequestIdMiddleware)]
