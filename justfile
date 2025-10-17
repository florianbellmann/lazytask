run:
	LAZYTASK_TASK_MANAGER="reminders-cli" LAZYTASK_LISTS="develop, Develop 2" uv run lazytask/__main__.py

dev: 
  LAZYTASK_LISTS="develop,develop2" uv run python lazytask
   
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
