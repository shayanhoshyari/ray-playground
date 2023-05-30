python -m venv .venv
. .venv/bin/activate

pip install  \
  ray[serve] \
  pydantic   \
  fastapi    \
  -e runtime