#!/usr/bin/env bash
set -euo pipefail

echo "=== Checking and setting up Idea-Man environment ==="

# Check Python 3
if ! command -v python3 &>/dev/null; then
  echo "Error: Python 3 is required but not installed." >&2
  exit 1
fi
echo "Python 3 version: $(python3 --version)"

# Check Node.js
if ! command -v node &>/dev/null; then
  echo "Error: Node.js is required but not installed." >&2
  exit 1
fi
echo "Node.js version: $(node --version)"

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

# Build static docs and validate site
echo "Building static site..."
node site/build.mjs

echo "Validating static site..."
node site/validate.mjs

echo "=== Environment setup complete! ==="
