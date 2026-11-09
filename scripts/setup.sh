#!/usr/bin/env bash
set -euo pipefail

echo "==> Setting up Idea-Man environment..."

# 1. Check Python runtime
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required but not installed." >&2
  exit 1
fi
echo "Python version: $(python3 --version)"

# 2. Check Node runtime
if ! command -v node &>/dev/null; then
  echo "ERROR: node is required but not installed." >&2
  exit 1
fi
echo "Node version: $(node --version)"

# 3. Create .env if missing from .env.example
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
fi

# 4. Build site artifacts if needed
echo "Building documentation site from site/..."
node site/build.mjs

echo "==> Environment setup complete! You can run tests or start the preview server."
