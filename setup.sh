#!/bin/bash

python -m venv .venv
. .venv/bin/activate
python -m pip install -U -r requirements.txt
