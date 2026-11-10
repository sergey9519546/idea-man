#!/usr/bin/env bash
set -euo pipefail

echo "=== Setting up Idea-Man environment ==="

# Check Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required (Python 3.9+ recommended, Python 3.12 verified)." >&2
  exit 1
fi

echo "Python version: $(python3 --version)"

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
  echo "Error: node is required (Node.js 18+ recommended, Node.js 22 verified)." >&2
  exit 1
fi

echo "Node version: $(node --version)"

# Build the static site if docs/ needs regeneration
echo "Building static site..."
node site/build.mjs

echo "Validating site structure and running node tests..."
node site/validate.mjs
node --test site/*.test.mjs

echo "Running Python test suite..."
python3 -m unittest discover -s tests

echo "Verifying worked examples..."
python3 eval/worked_examples.py --check

echo "=== Setup complete! All checks passed. ==="
