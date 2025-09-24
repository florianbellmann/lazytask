
dev:
    uv run main.py

run:
	uv run lazytask/__main__.py
   
run-watch:
  :x


test:
    uv run pytest 
     
test-watch:
	watchexec --exts py --restart "just test"

lint:
    cd lazytask && uv run mypy . --fix

check:
    uv run ruff check --fix

format:
    uv run ruff format
