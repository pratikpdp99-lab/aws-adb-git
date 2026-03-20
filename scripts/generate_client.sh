#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Generate the TypeScript API client from the FastAPI OpenAPI schema.
#
# Usage (from repo root):
#   bash scripts/generate_client.sh
#   make generate-client
#
# What it does:
#   1. Exports /openapi.json from the FastAPI app  → frontend/openapi.json
#   2. Runs openapi-typescript on the schema       → frontend/src/lib/api-types.ts
#
# Requirements:
#   pip install -r backend/requirements.txt
#   cd frontend && npm install
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "── Step 1: export OpenAPI schema from FastAPI ──────────────────────────"
python scripts/export_openapi.py

echo ""
echo "── Step 2: generate TypeScript types ──────────────────────────────────"
cd frontend
node_modules/.bin/openapi-typescript ../openapi.json -o src/lib/api-types.ts
cd ..

echo ""
echo "✓  Done."
echo "   frontend/openapi.json          ← FastAPI schema (commit this)"
echo "   frontend/src/lib/api-types.ts  ← generated TS types (commit this)"
echo ""
echo "   If you see type errors after regeneration, check frontend/src/lib/api.ts"
echo "   for any casts that need updating."
