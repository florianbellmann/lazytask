# <p>Lazytask</p>

![Pipeline](https://github.com/florianbellmann/lazytask/actions/workflows/go.yml/badge.svg)

Lazytask is a terminal task management interface inspired by [lazygit](https://github.com/jesseduffield/lazygit).

It's in POC / vibe coding state. My raspberry pi is in charge of development.

## ⚙️ Configuration

LazyTask can be configured using environment variables:

| Variable         | Description                                   | Default   |
| ---------------- | --------------------------------------------- | --------- |
| `LAZYTASK_LISTS` | Comma-separated list of reminder lists to use | `develop` |

Example:

```sh
LAZYTASK_LISTS=work,personal,shopping uv run python -m lazytask
```

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
