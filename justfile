test:
    uv run pytest 

dev:
    uv run main.py

run:
    uv run -m lazytask

lint:
    cd lazytask && uv run mypy . --fix

check:
    uv run ruff check --fix

format:
    uv run ruff format
