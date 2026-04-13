#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend"

PYTHON_BIN=""
POWERSHELL_BIN=""
for candidate in py python python3 /c/Windows/py.exe /c/Windows/python.exe /mnt/c/Windows/py.exe /mnt/c/Windows/python.exe; do
	if command -v "$candidate" >/dev/null 2>&1; then
		if "$candidate" -c "import pytest" >/dev/null 2>&1; then
			PYTHON_BIN="$candidate"
			break
		fi
	fi
done

if [[ -z "$PYTHON_BIN" ]]; then
	for shell_candidate in pwsh powershell.exe; do
		if command -v "$shell_candidate" >/dev/null 2>&1; then
			POWERSHELL_BIN="$shell_candidate"
			break
		fi
	done

	if [[ -z "$POWERSHELL_BIN" ]]; then
		echo "[deploy-dev] Could not find a Python executable with pytest installed or a PowerShell fallback."
		exit 1
	fi
fi

echo "[deploy-dev] Running backend tests"
if [[ -n "$PYTHON_BIN" ]]; then
	(cd "$BACKEND_DIR" && "$PYTHON_BIN" -m pytest -q tests)
else
	BACKEND_WIN_DIR="$BACKEND_DIR"
	if [[ "$BACKEND_WIN_DIR" =~ ^/mnt/([a-zA-Z])/(.*)$ ]]; then
		drive="${BASH_REMATCH[1]}"
		rest="${BASH_REMATCH[2]}"
		rest="${rest//\//\\}"
		BACKEND_WIN_DIR="${drive^^}:\\${rest}"
	fi
	"$POWERSHELL_BIN" -NoProfile -Command "Set-Location -LiteralPath '$BACKEND_WIN_DIR'; pytest -q tests"
fi

echo "[deploy-dev] Running infra tests"
(cd "$ROOT_DIR/src/infra" && npm test -- --runInBand --silent)

echo "[deploy-dev] Synthesizing CDK"
(cd "$ROOT_DIR/src/infra" && npm run synth)

echo "[deploy-dev] Completed. Use 'npm run deploy' in src/infra when ready."

