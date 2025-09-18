test:
    uv run pytest 

dev:
    uv run main.py

run:
    uv run -m lazytask

lint:
    cd lazytask && uv run mypy .

check:
    uv run ruff check

format:
    uv run ruff format
