# ─────────────────────────────────────────────────────────────────────────────
# TDM Deckers — convenience targets
# Run from the repo root.
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: help install dev backend frontend test test-backend test-databricks \
        generate-client lint build clean

help:                  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────
install:               ## Install all dependencies (backend + frontend)
	pip install -r backend/requirements.txt
	cd frontend && npm install --cache /tmp/npm-cache
	@echo "✓  Dependencies installed"
	@echo "   Copy .env.example → .env and fill in credentials"

# ── Development ───────────────────────────────────────────────────────────────
dev:                   ## Start backend + frontend (parallel)
	@bash scripts/dev.sh both

backend:               ## Start FastAPI backend only (port 8000)
	@bash scripts/dev.sh backend

frontend:              ## Start Next.js frontend only (port 3000)
	@bash scripts/dev.sh frontend

# ── Testing ───────────────────────────────────────────────────────────────────
test: test-backend test-databricks  ## Run all tests

test-backend:          ## Run FastAPI backend tests
	pytest backend/tests/ -v

test-databricks:       ## Run Databricks pipeline tests (requires pyspark)
	pytest databricks/tests/ -v

# ── OpenAPI client ────────────────────────────────────────────────────────────
generate-client:       ## Export OpenAPI schema + regenerate TypeScript client
	@bash scripts/generate_client.sh

# ── Frontend ──────────────────────────────────────────────────────────────────
lint:                  ## Lint frontend TypeScript
	cd frontend && npm run lint

build:                 ## Production build of frontend
	cd frontend && npm run build

# ── Databricks ────────────────────────────────────────────────────────────────
bundle-deploy-dev:     ## Deploy Databricks Asset Bundle to dev
	cd databricks && databricks bundle deploy --target dev

bundle-deploy-staging: ## Deploy Databricks Asset Bundle to staging
	cd databricks && databricks bundle deploy --target staging

# ── Infra ─────────────────────────────────────────────────────────────────────
tf-plan:               ## Terraform plan (AWS infra)
	cd infra/aws && terraform init -input=false && terraform plan -var="env=dev"

# ── Utilities ─────────────────────────────────────────────────────────────────
clean:                 ## Remove build artefacts
	rm -rf frontend/.next frontend/out
	find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	@echo "✓  Clean"
