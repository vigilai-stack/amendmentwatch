#!/bin/sh
set -e
python3 -m venv .venv 2>/dev/null || python -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --port 8000
