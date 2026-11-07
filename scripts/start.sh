#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Idea-Man preview server ==="

# Build site to ensure docs are up to date
node site/build.mjs

# Launch preview server on port 4317
echo "Launching local documentation server on port 4317..."
exec node site/preview.mjs
