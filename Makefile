setup:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

run:
	uv run python main.py

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f
