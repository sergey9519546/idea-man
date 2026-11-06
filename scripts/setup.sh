#!/usr/bin/env bash
set -euo pipefail

echo "=== Setting up Idea-Man Environment ==="

# Check Python version (requires Python 3.9+)
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "Found Python $PY_VER"
else
    echo "ERROR: python3 is not installed." >&2
    exit 1
fi

# Check Node.js version (requires Node.js 18+)
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v)
    echo "Found Node.js $NODE_VER"
else
    echo "ERROR: node is not installed." >&2
    exit 1
fi

# Build static landing site into docs/
echo "Building static landing site (node site/build.mjs)..."
node site/build.mjs

# Validate build
echo "Validating site build (node site/validate.mjs)..."
node site/validate.mjs

echo "=== Setup complete! ==="
echo "You can now run 'bash scripts/start.sh' to preview the landing site,"
echo "or run test suites with 'python3 -m unittest discover -s tests'."
