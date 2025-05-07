# <p>Lazytask</p>

![Pipeline](https://github.com/florianbellmann/lazytask/actions/workflows/go.yml/badge.svg)

Lazytask is a terminal task management interface inspired by [lazygit](https://github.com/jesseduffield/lazygit).

Because of time constraints this project is in a prototype state for now.

## 🛠️ Tech Stack

- [Go](https://go.dev/)
- [Bubbletea](https://github.com/charmbracelet/bubbletea/tree/master)

## 🧐 Roadmap

### MVP

- [x] Integrate swift adapter to work with apple reminders
- [x] Basic integration of bubbletea lists and text input, switching views etc.
- [x] Commands
  - [x] Adding a task by title
  - [x] Completing a task
- [x] Basic debugging with attach to process (vscode only)
- [x] Testing with recurring tasks
- [x] Switching between lists 

### Further development

- [x] Testing and stability v0.1
- [x] Restructure app
- [x] hot reloading https://github.com/charmbracelet/bubbletea/issues/150
- [ ] Restructure CLI part
- [ ] Implement app logging
- [ ] use message types for commands
      how to do comms with UI? 
	  https://chatgpt.com/c/681913f8-6bf4-800c-8f34-4bc08d042362
- [ ] User testing & feedback

- [ ] Implement commands
  - [ ] Edit dates
  - [ ] Move to tomorrow
  - [ ] Edit full card form
  - [ ] Edit descriptions
  - [ ] Edit tags
  - [ ] Edit prios
  - [ ] Edit flags
  - [ ] Refresh
- [ ] Handling of all tasks, not only overdue

- [ ] Building a basic ui
      https://leg100.github.io/en/posts/building-bubbletea-programs/
      https://github.com/dlvhdr/gh-dash
      https://github.com/bensadeh/circumflex
      Date picking: https://www.reddit.com/r/commandline/comments/1hrlrck/tui_datepicker/
- [ ] Async task handling with busy spinners, maybe add command queue
- [ ] Fix help pages initial app functionalities of fancy list etc
- [ ] Display of further infos: Tags, recurring, flags, prios, ...

- [ ] Github actions, go building and releases, tests are broken too
- [ ] Refactor functions to be testable and add proper testing
- [ ] Input hardening
- [ ] Debugging from inside nvim

- [ ] Build an nvim plugin for opening lazytask inside floating term

## 🧑🏻‍💻 Usage

```sh
./build
.build/./lazytask
```

## ⚙️ Configuration

LazyTask can be configured using environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `LISTS` | Comma-separated list of reminder lists to use | `develop` |

Example:
```sh
LISTS=work,personal,shopping .build/lazytask
```

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
