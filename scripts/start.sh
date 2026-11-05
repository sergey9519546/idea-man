#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-4317}"
HOST="${HOST:-127.0.0.1}"

echo "==> Starting Idea-Man documentation preview server on http://${HOST}:${PORT}..."

# Kill any existing server on this port
EXISTING_PID=$(lsof -t -i :"${PORT}" 2>/dev/null || true)
if [ -n "${EXISTING_PID}" ]; then
  echo "Stopping existing process on port ${PORT} (PID: ${EXISTING_PID})..."
  kill "${EXISTING_PID}" 2>/dev/null || true
  sleep 1
fi

exec node site/preview.mjs
