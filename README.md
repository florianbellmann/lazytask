# <p>Lazytask</p>

![Pipeline](https://github.com/florianbellmann/lazytask/actions/workflows/go.yml/badge.svg)

Lazytask is a terminal task management interface inspired by [lazygit](https://github.com/jesseduffield/lazygit).

Because of time constraints this project is in a prototype state for now.

## ⚙️ Configuration

LazyTask can be configured using environment variables:

| Variable | Description                                   | Default   |
| -------- | --------------------------------------------- | --------- |
| `LISTS`  | Comma-separated list of reminder lists to use | `develop` |

Example:

```sh
LISTS=work,personal,shopping .build/lazytask
```

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
