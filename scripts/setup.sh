#!/usr/bin/env bash
set -euo pipefail

echo "=== Idea-Man Environment Setup ==="

# Check Python version
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is not installed." >&2
  exit 1
fi
python3_ver=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Detected Python $python3_ver"

# Check Node version
if ! command -v node &>/dev/null; then
  echo "Error: node is not installed." >&2
  exit 1
fi
node_ver=$(node -v)
echo "Detected Node.js $node_ver"

# Ensure .env exists from template if not already present
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
  fi
fi

# Build static documentation and evidence website
echo "Building static site..."
node site/build.mjs

# Validate static site build integrity
echo "Validating static site..."
node site/validate.mjs

echo "=== Setup complete! ==="
echo "Run './scripts/start.sh' to start the local preview server."
