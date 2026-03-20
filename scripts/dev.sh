#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Start the full TDM platform stack for local development.
#
# Usage:
#   bash scripts/dev.sh          # starts both backend and frontend
#   bash scripts/dev.sh backend  # backend only  (http://localhost:8000)
#   bash scripts/dev.sh frontend # frontend only (http://localhost:3000)
#   bash scripts/dev.sh docs     # print API docs URL only
#
# Prerequisites:
#   pip install -r backend/requirements.txt
#   cp .env.example .env && fill in DATABRICKS_HOST / DATABRICKS_TOKEN
#   cd frontend && npm install
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MODE="${1:-both}"

start_backend() {
  echo "▶  Backend  → http://localhost:8000"
  echo "   API docs → http://localhost:8000/docs"
  uvicorn backend.app.main:app --reload --port 8000
}

start_frontend() {
  echo "▶  Frontend → http://localhost:3000"
  cd frontend && npm run dev
}

case "$MODE" in
  backend)
    start_backend
    ;;
  frontend)
    start_frontend
    ;;
  docs)
    echo "API docs: http://localhost:8000/docs"
    echo "OpenAPI : http://localhost:8000/openapi.json"
    ;;
  both|*)
    # Run both in parallel; kill both on Ctrl-C
    trap 'kill %1 %2 2>/dev/null; exit' INT TERM

    echo "Starting TDM platform..."
    echo ""

    (start_backend) &
    sleep 1
    (start_frontend) &

    wait
    ;;
esac
