import logging

from runtime_env.pydev import connect_to_pydev
from starlette.middleware import Middleware

logger = logging.getLogger("ray.serve")

def proxy_callback() -> list[Middleware]:
    # How to pass the pydev info here to connect to?
    # connect_to_pydev( ... )
    return []
