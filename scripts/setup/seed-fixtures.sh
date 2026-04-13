#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export DEMO_MODE=true
export AWS_REGION_NAME="${AWS_REGION_NAME:-us-east-1}"
export RECOMMENDATIONS_TABLE_NAME="${RECOMMENDATIONS_TABLE_NAME:-finops-recommendations}"

echo "[seed-fixtures] Seeding recommendation fixtures into DynamoDB table: $RECOMMENDATIONS_TABLE_NAME"
python "$ROOT_DIR/scripts/seed/seed-dynamo.py"

echo "[seed-fixtures] Done"

