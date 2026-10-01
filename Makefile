.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

PYTHON ?= python3
VENV ?= .venv
PORT ?= 8735
ENV ?= dev
BACKUP_DIR ?= backups
ifeq ($(ENV),prod)
COMPOSE := docker compose --env-file .env.production -f docker/compose.production.yaml
else ifeq ($(ENV),dev)
COMPOSE := docker compose $(if $(wildcard .env),--env-file .env) -f docker/compose.yaml
else
$(error ENV must be dev or prod)
endif

.PHONY: help setup install dev test test-js validate check config build up down restart logs ps shell docker-test smoke backup restore prod-up prod-down

help: ## Show available commands (ENV=dev by default; ENV=prod selects production)
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)

setup: $(VENV)/bin/python ## Install locked development dependencies locally
	$(VENV)/bin/python -m pip install -r backend/requirements/dev.lock

install: $(VENV)/bin/python ## Install locked runtime dependencies locally
	$(VENV)/bin/python -m pip install -r backend/requirements/runtime.lock

dev: ## Run local FastAPI with reload (PORT=8735)
	ACADEMY_DEBUG=1 ACADEMY_CPP=$${ACADEMY_CPP:-0} ACADEMY_SECURE_COOKIES=0 PORT=$(PORT) $(VENV)/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port $(PORT) --reload --no-proxy-headers

test: ## Run Python suite (includes Node regressions when available)
	$(VENV)/bin/python -m pytest -q

test-js: ## Run all dependency-free Node regression suites
	node --test tests/frontend.test.cjs tests/dsa-store.test.cjs tests/dsa-traces.test.cjs

validate: ## Validate authored DSA content
	$(VENV)/bin/python tools/validate_dsa.py

check: test-js test validate ## Run complete local checks

config: ## Validate selected Compose configuration
	$(COMPOSE) config --quiet

build: ## Build selected Docker image
	$(COMPOSE) build --pull

up: ## Build and start selected stack, waiting for health
	$(COMPOSE) up -d --build --wait --wait-timeout 120

down: ## Stop selected stack; preserve database and certificate volumes
	$(COMPOSE) down

restart: ## Restart selected stack
	$(COMPOSE) restart

logs: ## Follow selected stack logs
	$(COMPOSE) logs --follow --tail=100

ps: ## Show selected stack status
	$(COMPOSE) ps

shell: ## Open a shell in the running application
	$(COMPOSE) exec app /bin/sh

docker-test: ## Run tests in a disposable development container
	docker compose -f docker/compose.yaml run --build --rm --no-deps -T -e ACADEMY_DB=/tmp/test.db app python -m pytest -q

smoke: ## Check a running deployment (URL=http://localhost:8735 by default)
	$(PYTHON) tools/smoke.py --url "$(or $(URL),http://localhost:8735)"

backup: ## Save a consistent live SQLite snapshot from selected stack
	@mkdir -p "$(BACKUP_DIR)"
	@umask 077; dest="$(BACKUP_DIR)/academy-$(ENV)-$$(date -u +%Y%m%dT%H%M%S)-$$$$.db"; \
	trap 'rm -f "$$dest.tmp"' EXIT; \
	$(COMPOSE) exec -T app python tools/database.py backup > "$$dest.tmp"; \
	mv "$$dest.tmp" "$$dest"; echo "Backup saved: $$dest"

restore: ## Replace selected database from FILE=backup.db (stops app first)
	@test -n "$(FILE)" && test -f "$(FILE)" || { echo 'Usage: make restore FILE=backups/academy-....db [ENV=prod]'; exit 1; }
	$(PYTHON) tools/database.py validate "$(FILE)"
	$(COMPOSE) stop app
	$(COMPOSE) run --rm --no-deps -T app python tools/database.py restore < "$(FILE)"
	$(COMPOSE) up -d --no-build --wait --wait-timeout 120

prod-up: ## Build and start production HTTPS stack
	$(MAKE) ENV=prod up

prod-down: ## Stop production stack, keeping persistent volumes
	$(MAKE) ENV=prod down
