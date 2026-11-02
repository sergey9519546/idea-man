#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Idea-Man documentation & site preview server ==="
echo "Serving docs on http://127.0.0.1:4317 (Press Ctrl+C to stop)"

node site/preview.mjs
