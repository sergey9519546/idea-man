#!/usr/bin/env bash
set -euo pipefail

echo "=== Setting up Idea-Man environment ==="

# Check Python 3.9+
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not installed." >&2
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PYTHON_VERSION"

# Check Node.js 18+
if ! command -v node >/dev/null 2>&1; then
  echo "Error: node is required but not installed." >&2
  exit 1
fi

NODE_VERSION=$(node -v)
echo "Found Node.js $NODE_VERSION"

# Check npm
if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is required but not installed." >&2
  exit 1
fi

# Build static site if not already built or to ensure up-to-date docs
echo "Building and validating static documentation site..."
node site/build.mjs
node site/validate.mjs

echo "=== Idea-Man environment setup complete! ==="
