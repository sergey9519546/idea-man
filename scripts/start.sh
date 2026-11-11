#!/usr/bin/env bash
set -euo pipefail

# Load environment variables if .env exists
if [ -f .env ]; then
  # Export non-comment lines
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${PORT:-4317}"
HOST="${HOST:-127.0.0.1}"

# Kill any existing process on the specified port
if command -v lsof &>/dev/null; then
  existing_pid=$(lsof -t -i :"$PORT" 2>/dev/null || true)
  if [ -n "$existing_pid" ]; then
    echo "Stopping existing process on port $PORT (PID $existing_pid)..."
    kill "$existing_pid" 2>/dev/null || true
    sleep 1
  fi
fi

# Ensure site is built
if [ ! -d docs ] || [ ! -f docs/index.html ]; then
  echo "Site build not found. Running setup..."
  bash scripts/setup.sh
fi

echo "Starting Idea-Man preview server on http://$HOST:$PORT..."
exec node site/preview.mjs
