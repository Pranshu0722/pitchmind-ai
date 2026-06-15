# ============================================================
# PitchMind AI — Makefile
# ============================================================
.DEFAULT_GOAL := help
SHELL := bash

# Colours
CYAN  := \033[0;36m
RESET := \033[0m

.PHONY: help dev dev-infra stop logs \
        lint format typecheck test test-unit test-integration \
        migrate migrate-rollback seed \
        build clean

help:
	@echo ""
	@echo "$(CYAN)PitchMind AI$(RESET)"
	@echo ""
	@echo "  Dev:"
	@echo "    make dev              Start full stack (build + up)"
	@echo "    make dev-infra        Start infrastructure only (db, redis, minio, mlflow)"
	@echo "    make stop             Stop all containers"
	@echo "    make logs             Tail all container logs"
	@echo ""
	@echo "  Quality:"
	@echo "    make lint             Run ruff + eslint"
	@echo "    make format           Run ruff-format + prettier"
	@echo "    make typecheck        Run mypy + tsc"
	@echo "    make test             Run all tests"
	@echo "    make test-unit        Run unit tests only"
	@echo "    make test-integration Run integration tests only"
	@echo ""
	@echo "  Database:"
	@echo "    make migrate          Apply Alembic migrations"
	@echo "    make migrate-rollback Roll back last migration"
	@echo "    make seed             Seed demo data"
	@echo ""
	@echo "  Build:"
	@echo "    make build            Build all Docker images"
	@echo "    make clean            Remove containers, volumes, caches"
	@echo ""

# ------------------------------------------------------------------
# Development
# ------------------------------------------------------------------

dev:
	docker compose up --build -d
	@echo "$(CYAN)Stack is up. API: http://localhost:8000  Web: http://localhost:5173$(RESET)"

dev-infra:
	docker compose up -d db cache minio mlflow prometheus grafana
	@echo "$(CYAN)Infrastructure up. MLflow: http://localhost:5000  MinIO: http://localhost:9001$(RESET)"

stop:
	docker compose down

logs:
	docker compose logs -f

# ------------------------------------------------------------------
# Code quality
# ------------------------------------------------------------------

lint:
	cd backend && uv run ruff check src/ tests/
	cd frontend && npm run lint

format:
	cd backend && uv run ruff format src/ tests/
	cd frontend && npm run format

typecheck:
	cd backend && uv run mypy src/pitchmind
	cd frontend && npm run typecheck

# ------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------

test:
	$(MAKE) test-unit
	$(MAKE) test-integration

test-unit:
	cd backend && uv run pytest tests/unit -v --tb=short

test-integration:
	cd backend && uv run pytest tests/integration -v --tb=short

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------

migrate:
	cd backend && uv run alembic upgrade head

migrate-rollback:
	cd backend && uv run alembic downgrade -1

seed:
	cd backend && uv run python scripts/seed_demo_match.py

# ------------------------------------------------------------------
# Build
# ------------------------------------------------------------------

build:
	docker compose build

clean:
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules dist .cache node_modules 2>/dev/null || true
	@echo "$(CYAN)Clean complete.$(RESET)"
