import time

import ray.serve
from runtime_env.model import Model
from runtime_env.pydev import PYDEV_CONFIG_KEY, create_pydev_config

# Create pydev config if running in vscode.
pydev_config = create_pydev_config()

# We can pass the pydev_config to the deployment via the bind() function.
# The constructor of `Model` will then connect to vscode and we can put breakpoints in the debugger.
deploy = Model.bind(pydev_config)  # type: ignore

# How can we send the pydev_config to the HTTPProxy?
# I can serialize as string and pass as env var in runtime_env, but I cannot send runtime_env to HTTPPRoxy either.
# Same for SERVE_HTTP_PROXY_CALLBACK_IMPORT_PATH, how can I pass a runtime_env for HTTPProxy with this value inside it?
ray.init(runtime_env={"env_vars": {PYDEV_CONFIG_KEY: pydev_config.json()}})
ray.serve.run(deploy)

try:
    while True:
        # Block, letting Ray print logs to the terminal
        time.sleep(10)
finally:
    ray.shutdown()
