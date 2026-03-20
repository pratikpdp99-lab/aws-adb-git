#!/usr/bin/env python3
"""
Export FastAPI OpenAPI schema to frontend/openapi.json.
Run from the repo root:  python scripts/export_openapi.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.main import app  # noqa: E402 — path must be inserted first

schema = app.openapi()

out = Path(__file__).parent.parent / "frontend" / "openapi.json"
out.write_text(json.dumps(schema, indent=2))
print(f"✓  OpenAPI schema written → {out}")
print(f"   Routes : {len(schema.get('paths', {}))} paths")
print(f"   Schemas: {len(schema.get('components', {}).get('schemas', {}))} models")
