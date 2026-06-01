# =============================================================================
# ExecutiveAI — Makefile
# Usage: make <target>
# Run `make help` to see all available targets.
# =============================================================================

# Shell settings
SHELL := /bin/bash
.DEFAULT_GOAL := help

# Colours for terminal output
RESET   := \033[0m
BOLD    := \033[1m
GREEN   := \033[32m
YELLOW  := \033[33m
CYAN    := \033[36m
RED     := \033[31m

# Docker Compose command (supports both v1 and v2)
DC := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

# Project name used by Docker Compose
PROJECT := executiveai

# Backend service name inside Docker
BACKEND_SERVICE  := backend
DB_SERVICE       := postgres
WORKER_SERVICE   := celery_worker

# =============================================================================
# HELP
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "$(BOLD)$(CYAN)ExecutiveAI — Make Targets$(RESET)"
	@echo "$(CYAN)────────────────────────────────────────────────────────$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# SETUP
# =============================================================================

.PHONY: setup
setup: check-prereqs env-copy dirs build up wait-healthy migrate seed ## Full first-time setup (build → start → migrate → seed)
	@echo ""
	@echo "$(GREEN)$(BOLD)Setup complete!$(RESET)"
	@echo ""
	@echo "  Frontend : http://localhost:3000"
	@echo "  Backend  : http://localhost:8000"
	@echo "  API Docs : http://localhost:8000/docs"
	@echo ""

.PHONY: check-prereqs
check-prereqs: ## Check that required tools are installed
	@echo "$(CYAN)Checking prerequisites...$(RESET)"
	@command -v docker   >/dev/null 2>&1 || (echo "$(RED)docker not found$(RESET)"   && exit 1)
	@command -v git      >/dev/null 2>&1 || (echo "$(RED)git not found$(RESET)"      && exit 1)
	@docker info         >/dev/null 2>&1 || (echo "$(RED)Docker daemon not running$(RESET)" && exit 1)
	@echo "$(GREEN)All prerequisites satisfied.$(RESET)"

.PHONY: env-copy
env-copy: ## Copy .env.example to .env if .env doesn't exist
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW).env created from .env.example — please review and edit it.$(RESET)"; \
	else \
		echo "$(GREEN).env already exists, skipping.$(RESET)"; \
	fi

.PHONY: dirs
dirs: ## Create required host-side directories
	@mkdir -p infrastructure/nginx/ssl
	@echo "$(GREEN)Directories ready.$(RESET)"

# =============================================================================
# DOCKER COMPOSE LIFECYCLE
# =============================================================================

.PHONY: build
build: ## Build (or rebuild) all Docker images
	@echo "$(CYAN)Building images...$(RESET)"
	$(DC) build --parallel

.PHONY: up
up: ## Start all services in detached mode
	@echo "$(CYAN)Starting services...$(RESET)"
	$(DC) up -d

.PHONY: up-build
up-build: ## Build and start all services
	$(DC) up -d --build

.PHONY: down
down: ## Stop and remove containers (data volumes preserved)
	@echo "$(CYAN)Stopping services...$(RESET)"
	$(DC) down

.PHONY: down-volumes
down-volumes: ## Stop containers AND remove all volumes (DESTROYS DATA)
	@echo "$(RED)$(BOLD)WARNING: This will destroy all data volumes!$(RESET)"
	@read -p "Are you sure? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		$(DC) down -v; \
		echo "$(GREEN)Volumes removed.$(RESET)"; \
	else \
		echo "Aborted."; \
	fi

.PHONY: restart
restart: down up ## Restart all services

.PHONY: restart-backend
restart-backend: ## Restart only the backend service
	$(DC) restart $(BACKEND_SERVICE)

.PHONY: restart-worker
restart-worker: ## Restart only the Celery worker
	$(DC) restart $(WORKER_SERVICE)

.PHONY: ps
ps: ## Show running service status
	$(DC) ps

.PHONY: wait-healthy
wait-healthy: ## Wait until postgres and redis are healthy
	@echo "$(CYAN)Waiting for services to become healthy...$(RESET)"
	@for i in $$(seq 1 30); do \
		if $(DC) ps $(DB_SERVICE) | grep -q "healthy"; then \
			echo "$(GREEN)PostgreSQL is healthy.$(RESET)"; \
			break; \
		fi; \
		echo "  Waiting for PostgreSQL... ($$i/30)"; \
		sleep 3; \
	done

# =============================================================================
# LOGS
# =============================================================================

.PHONY: logs
logs: ## Tail logs from all services
	$(DC) logs -f --tail=100

.PHONY: logs-backend
logs-backend: ## Tail backend logs
	$(DC) logs -f --tail=100 $(BACKEND_SERVICE)

.PHONY: logs-frontend
logs-frontend: ## Tail frontend logs
	$(DC) logs -f --tail=100 frontend

.PHONY: logs-worker
logs-worker: ## Tail Celery worker logs
	$(DC) logs -f --tail=100 $(WORKER_SERVICE)

.PHONY: logs-nginx
logs-nginx: ## Tail Nginx logs
	$(DC) logs -f --tail=100 nginx

.PHONY: logs-db
logs-db: ## Tail PostgreSQL logs
	$(DC) logs -f --tail=100 $(DB_SERVICE)

# =============================================================================
# DATABASE
# =============================================================================

.PHONY: migrate
migrate: ## Run Alembic database migrations (upgrade head)
	@echo "$(CYAN)Running database migrations...$(RESET)"
	$(DC) exec $(BACKEND_SERVICE) alembic upgrade head
	@echo "$(GREEN)Migrations complete.$(RESET)"

.PHONY: migrate-create
migrate-create: ## Create a new Alembic migration (MSG="description")
	@if [ -z "$(MSG)" ]; then echo "$(RED)Usage: make migrate-create MSG=\"your migration description\"$(RESET)" && exit 1; fi
	$(DC) exec $(BACKEND_SERVICE) alembic revision --autogenerate -m "$(MSG)"

.PHONY: migrate-downgrade
migrate-downgrade: ## Downgrade by one migration step
	$(DC) exec $(BACKEND_SERVICE) alembic downgrade -1

.PHONY: migrate-history
migrate-history: ## Show Alembic migration history
	$(DC) exec $(BACKEND_SERVICE) alembic history --verbose

.PHONY: migrate-current
migrate-current: ## Show current Alembic revision
	$(DC) exec $(BACKEND_SERVICE) alembic current

# =============================================================================
# SEEDING
# =============================================================================

.PHONY: seed
seed: ## Seed the database with demo data
	@echo "$(CYAN)Seeding demo data...$(RESET)"
	@bash scripts/seed_demo.sh
	@echo "$(GREEN)Demo data seeded.$(RESET)"

.PHONY: seed-reset
seed-reset: ## Drop all data and re-seed (DESTRUCTIVE)
	@echo "$(RED)Resetting and re-seeding database...$(RESET)"
	$(DC) exec $(BACKEND_SERVICE) python -m app.scripts.reset_and_seed

# =============================================================================
# SHELLS
# =============================================================================

.PHONY: shell-backend
shell-backend: ## Open a bash shell inside the backend container
	$(DC) exec $(BACKEND_SERVICE) bash

.PHONY: shell-db
shell-db: ## Open a psql session against the database
	$(DC) exec $(DB_SERVICE) psql -U $${POSTGRES_USER:-executiveai} -d $${POSTGRES_DB:-executiveai_db}

.PHONY: shell-redis
shell-redis: ## Open a redis-cli session
	$(DC) exec redis redis-cli

.PHONY: python
python: ## Open a Python REPL inside the backend container
	$(DC) exec $(BACKEND_SERVICE) python

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: test-backend test-frontend ## Run all tests

.PHONY: test-backend
test-backend: ## Run backend pytest suite
	@echo "$(CYAN)Running backend tests...$(RESET)"
	$(DC) exec $(BACKEND_SERVICE) pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

.PHONY: test-frontend
test-frontend: ## Run frontend Jest/Vitest suite
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	$(DC) exec frontend npm test -- --watchAll=false

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests with Playwright
	$(DC) exec frontend npm run test:e2e

# =============================================================================
# LINTING & FORMATTING
# =============================================================================

.PHONY: lint
lint: lint-backend lint-frontend ## Lint all code

.PHONY: lint-backend
lint-backend: ## Run ruff + black check on backend
	@echo "$(CYAN)Linting backend...$(RESET)"
	$(DC) exec $(BACKEND_SERVICE) ruff check app/
	$(DC) exec $(BACKEND_SERVICE) black --check app/

.PHONY: lint-frontend
lint-frontend: ## Run ESLint on frontend
	@echo "$(CYAN)Linting frontend...$(RESET)"
	$(DC) exec frontend npm run lint

.PHONY: format
format: format-backend format-frontend ## Auto-format all code

.PHONY: format-backend
format-backend: ## Run black + isort on backend
	$(DC) exec $(BACKEND_SERVICE) black app/
	$(DC) exec $(BACKEND_SERVICE) isort app/

.PHONY: format-frontend
format-frontend: ## Run Prettier on frontend
	$(DC) exec frontend npm run format

# =============================================================================
# PRODUCTION UTILITIES
# =============================================================================

.PHONY: ssl-self-signed
ssl-self-signed: ## Generate a self-signed SSL certificate for local HTTPS
	@echo "$(CYAN)Generating self-signed certificate...$(RESET)"
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout infrastructure/nginx/ssl/privkey.pem \
		-out  infrastructure/nginx/ssl/fullchain.pem \
		-subj "/C=US/ST=Dev/L=Local/O=ExecutiveAI/CN=localhost"
	@echo "$(GREEN)Certificate written to infrastructure/nginx/ssl/$(RESET)"

.PHONY: backup-db
backup-db: ## Create a timestamped PostgreSQL dump
	@mkdir -p backups
	$(DC) exec $(DB_SERVICE) pg_dump -U $${POSTGRES_USER:-executiveai} \
		$${POSTGRES_DB:-executiveai_db} | gzip > backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "$(GREEN)Backup saved to backups/$(RESET)"

.PHONY: restore-db
restore-db: ## Restore a database backup (FILE=backups/backup_xyz.sql.gz)
	@if [ -z "$(FILE)" ]; then echo "$(RED)Usage: make restore-db FILE=backups/backup_xyz.sql.gz$(RESET)" && exit 1; fi
	gunzip -c $(FILE) | $(DC) exec -T $(DB_SERVICE) psql -U $${POSTGRES_USER:-executiveai} \
		$${POSTGRES_DB:-executiveai_db}

.PHONY: clean
clean: ## Remove Docker build cache and unused images
	docker system prune -f
	docker image prune -f

.PHONY: clean-all
clean-all: down-volumes clean ## Full clean: volumes + cache (DESTRUCTIVE)
