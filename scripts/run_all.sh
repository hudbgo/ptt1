#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACK_PID=$!

cd desktop
npm run dev:desktop

trap 'kill $BACK_PID' EXIT
