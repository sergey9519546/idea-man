#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Idea-Man Landing Site Preview ==="

# Check that docs/index.html exists; if not, build it first
if [ ! -f "docs/index.html" ]; then
    echo "Site output not found in docs/. Running build first..."
    node site/build.mjs
fi

# Launch preview server
echo "Starting preview server on http://127.0.0.1:4317 ..."
exec node site/preview.mjs
