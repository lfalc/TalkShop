#!/usr/bin/env bash
# Emulate Render build: fresh venv, pip install -r requirements.txt, verify app imports.
# Run from repo root: ./scripts/render_build_test.sh
set -e
cd "$(dirname "$0")/.."
VENV_DIR="${VENV_DIR:-.render-build-venv}"
echo "=== Render build test ==="
echo "Using venv: $VENV_DIR"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1090
. "$VENV_DIR/bin/activate"
echo "=== pip install -r requirements.txt ==="
pip install -q -r requirements.txt
echo "=== Checking app import (PYTHONPATH=src python -c 'from api.main import app') ==="
PYTHONPATH=src python -c "from api.main import app; print('OK: app imported')"
echo "=== Render build test passed ==="
if [[ "$VENV_DIR" == ".render-build-venv" ]]; then
  rm -rf "$VENV_DIR"
fi
