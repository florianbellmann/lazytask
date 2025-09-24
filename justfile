run:
	uv run lazytask/__main__.py

dev: 
  LAZYTASK_DEFAULT_LIST="develop" LAZYTASK_LISTS="develop,develop2" uv run python lazytask
   
dev-watch:
  watchexec --exts py --restart "just dev"

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
