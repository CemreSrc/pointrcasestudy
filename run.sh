#!/usr/bin/env bash
set -euo pipefail
# Simple helper to run the FastAPI app locally
# Usage: ./run.sh [host] [port]
HOST=${1:-127.0.0.1}
PORT=${2:-8000}
exec uvicorn app.main:app --reload --host "$HOST" --port "$PORT"