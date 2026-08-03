.PHONY: help install dev run test test-coverage lint format typecheck pre-commit docker-up docker-down clean

PYTHON ?= python3
PYTHONPATH := backend

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install the package into the active environment
	$(PYTHON) -m pip install -e ".[dev]"

dev: ## Run the API server with live reload
	PYTHONPATH=$(PYTHONPATH) uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test: ## Run the full test suite
	PYTHONPATH=$(PYTHONPATH) pytest

test-coverage: ## Run the full test suite with coverage report
	PYTHONPATH=$(PYTHONPATH) pytest --cov=app --cov-report=term-missing

lint: ## Lint the backend with ruff
	ruff check backend

format: ## Auto-format the backend with ruff
	ruff check backend --fix
	ruff format backend

doctor: ## Run lint + type check
	ruff check backend && mypy backend/app

pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

docker-up: ## Start Mongo + Redis + app + Prometheus
	docker compose -f docker/docker-compose.yml up --build

docker-down: ## Tear down the docker stack
	docker compose -f docker/docker-compose.yml down