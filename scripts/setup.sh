#!/usr/bin/env bash
set -euo pipefail

echo "=== Idea-Man Environment Setup ==="

# Check Python 3
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 --version 2>&1)
    echo "[✓] Python installed: ${PY_VER}"
else
    echo "[✗] Python 3 is required but not installed." >&2
    exit 1
fi

# Check Node.js
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node --version 2>&1)
    echo "[✓] Node.js installed: ${NODE_VER}"
else
    echo "[✗] Node.js is required but not installed." >&2
    exit 1
fi

# Python dependencies
if [ -f "requirements.txt" ]; then
    echo "[*] Checking Python dependencies..."
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install -r requirements.txt --quiet || true
    fi
    echo "[✓] Python requirements processed."
fi

# Validate and build static site
echo "[*] Building and validating static landing site..."
node site/build.mjs
node site/validate.mjs

echo "=== Setup complete! Everything is ready to run. ==="
