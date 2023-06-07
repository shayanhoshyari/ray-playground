import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any

import pydantic

logger = logging.getLogger(__name__)

PYDEV_CONFIG_KEY = "COLLIGO_PYDEV_CONFIG"


class PydevConfig(pydantic.BaseModel):
    sys_path: str
    client: str
    port: int
    client_access_token: str
    ppid: int


def get_debugpy() -> Any:
    try:
        return importlib.import_module("debugpy")
    except Exception:
        return None


def break_in_vscode() -> None:
    """Breaks into the debugger if it is connected."""
    debugpy = get_debugpy()
    if debugpy is None:
        return
    if debugpy.is_client_connected():
        debugpy.breakpoint()


def connect_to_pydev(config: PydevConfig) -> None:
    sys_path = config.sys_path
    sys.path.append(sys_path)

    logging.info(f"Added debupy sys path {sys_path}")

    debugpy = get_debugpy()
    if debugpy is None:
        logger.error(
            "debugpy was not available to the raylet even after adding the required syspath. Bailing out.",
            exc_info=True,
        )
        return

    logging.info("Imported debugpy")

    if debugpy.is_client_connected():
        logger.warning("debugpy client already connected.")
        return

    client = config.client
    port = config.port
    client_access_token = config.client_access_token

    pydevd = debugpy.server.api.pydevd
    pydevd.SetupHolder.setup = {
        "ppid": config.ppid,
        "client": client,
        "port": port,
        "client-access-token": client_access_token,
    }

    logging.info(f"Connecting to debugpy at {client}:{port}")
    debugpy.connect([client, port], access_token=client_access_token)

    logger.info("Waiting for debugger connection.")
    debugpy.wait_for_client()
    logger.info("Connected to the debugger.")


def create_pydev_config() -> PydevConfig | None:
    debugpy = get_debugpy()
    if debugpy is None:
        logger.info("Pydev is not available, vs code debug support is not available.")
        return None

    if not debugpy.is_client_connected():
        logger.info("No VS code was available during boot.")
        return None

    pydevd = debugpy.server.api.pydevd
    setup = pydevd.SetupHolder.setup

    return PydevConfig(
        ppid=os.getpid(),
        sys_path=str(Path(debugpy.__file__).absolute().parents[1]),
        client=setup.get("client"),
        port=setup.get("port"),
        client_access_token=setup.get("client-access-token"),
    )
