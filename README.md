# <p>Lazytask</p>

![Pipeline](https://github.com/florianbellmann/lazytask/actions/workflows/ci.yml/badge.svg)

Lazytask is a terminal task management interface inspired by [lazygit](https://github.com/jesseduffield/lazygit).

It's in POC / vibe coding state. My raspberry pi is in charge of development.

## ⚙️ Configuration

LazyTask can be configured using environment variables:

| Variable         | Description                                   | Default   |
| ---------------- | --------------------------------------------- | --------- |
| `LAZYTASK_LISTS` | Comma-separated list of reminder lists to use | `develop` |
| `LAZYTASK_TASK_MANAGER` | Task manager backend to use (`mock` or `reminders-cli`) | `mock` |

Example:

```sh
LAZYTASK_LISTS=work,personal,shopping uv run python -m lazytask

# Use the reminders-cli backend (enabled by default in `just run`)
LAZYTASK_TASK_MANAGER=reminders-cli LAZYTASK_LISTS=develop uv run python -m lazytask
```

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
