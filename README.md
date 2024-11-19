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

- [ ] User testing & feedback
- [ ] restructure app
- [ ] Implement app logging
- [ ] use message types for commands

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
      https://github.com/dlvhdr/gh-dash
      https://github.com/bensadeh/circumflex
- [ ] Async task handling with busy spinners, maybe add command queue
- [ ] Fix help pages initial app functionalities of fancy list etc
- [ ] Display of further infos: Tags, recurring, flags, prios, ...

- [ ] Github actions, go building and releases, tests are broken too
- [ ] Refactor functions to be testable and add proper testing
- [ ] Input hardening
- [ ] Debugging from inside nvim

## 🧑🏻‍💻 Usage

```sh
./build
.build/./lazytask
```

## ➤ License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
