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

Well, at this stage I now need to give the app a proper harness with myPyRough check format and then a lot of tests. So my next approach would be a kind of TDD style workflow, where I define out all of the tests that I want to see and all of the features that I want the app to have, and then slowly but steady get it to where it needs to be. This is a bit more tedious to do on the phone, so I think I can can do the vibe coding continuing on the phone when I have the harness. So for now I will leave it as is. I made some good progress and also some some learnings on what I can do, what I should do, but that's it for now.


testing and bug fixes 

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
