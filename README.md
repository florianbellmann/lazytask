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

i need to be able to create a new task zhrough a singular prompt. mesning running a quick cli prompt for getting the title and confirming the creation. then the process stops. this should be independent from the normal main application. 
recurring tasks 
loading indicators

testing and bug fixes 

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
