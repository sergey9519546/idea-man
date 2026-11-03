#!/usr/bin/env bash
set -euo pipefail

PORT=${PORT:-4317}
HOST=${HOST:-127.0.0.1}

echo "=== Starting Idea-Man Local Preview Server ==="

# Ensure existing process on port is stopped
if command -v lsof >/dev/null 2>&1; then
    PID=$(lsof -t -i :${PORT} 2>/dev/null || true)
    if [ -n "${PID}" ]; then
        echo "[*] Killing existing process on port ${PORT} (PID ${PID})..."
        kill "${PID}" 2>/dev/null || true
        sleep 1
    fi
fi

# Build static site if docs/index.html is missing
if [ ! -f "docs/index.html" ]; then
    echo "[*] Building site docs..."
    node site/build.mjs
fi

echo "[*] Launching preview server at http://${HOST}:${PORT} ..."
exec node site/preview.mjs
