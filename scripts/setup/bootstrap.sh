#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[bootstrap] Installing backend dependencies"
python -m pip install -r "$ROOT_DIR/src/backend/requirements.txt"
python -m pip install -r "$ROOT_DIR/src/backend/requirements-dev.txt"

echo "[bootstrap] Installing frontend dependencies"
(cd "$ROOT_DIR/src/frontend" && npm install)

echo "[bootstrap] Installing infra dependencies"
(cd "$ROOT_DIR/src/infra" && npm install)

echo "[bootstrap] Setup complete"

