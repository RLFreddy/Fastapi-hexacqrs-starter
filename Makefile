.PHONY: install test lint lint-fix run migrate migrate-new shell

install:
	uv sync

test:
	uv run pytest -v --tb=short

lint:
	uv run ruff check src tests

lint-fix:
	uv run ruff check --fix src tests

run:
	uv run python -m src.main

migrate:
	uv run alembic upgrade head

migrate-new:
	uv run alembic revision --autogenerate -m "$(name)"

shell:
	uv run python
