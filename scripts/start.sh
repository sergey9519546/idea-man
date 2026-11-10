#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-4317}"

echo "Starting Idea-Man site preview server on port ${PORT}..."
exec node site/preview.mjs
