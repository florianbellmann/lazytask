# LazyTask Helper Guide

## General Guidelines

- Always use descriptive variable names, e.g. `customerName` instead of `name`
- Don't fix typescript errors with 'any' type, use the correct type instead
- Always use `uv` no `requirements.txt` or `poerty`
- Always try to use a declarative approach. Have config objects etc.
- Use declarative programming where possible, e.g. use config objects and `map`, `filter`, `reduce` instead of `forEach`
- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

- Test behavior, not implementation
- One assertion per test when possible
- Clear test names describing scenario
- Use existing test utilities/helpers
- Tests should be deterministic

Respext the[dev guide](./DEVELOPER_GUIDE.md) !!!
- When adding logging during fixing tests. always add them in a way that they only get executed running pytest. then they can also stay in the code to help future test fixing

Run `just check`,`just lint` and `just test` before finishing your task

**NEVER**:

- Use `--no-verify` to bypass commit hooks
- Disable tests instead of fixing them
- Make assumptions - verify with existing code

- Follows domain-driven design principles
- Domain-driven design: Keep domain logic in domain/, use dependency
  injection and keep concrete implementations in infrastructure/

## Project Specific

Inspect the Reminder CLI submodule and see which functionalities are available there.

Always run the app through `uv`.

I want to build an application that can be a terminal interface for me to
work with task management. In this repository you find a sub-module for the
Reminder CLI to handle Apple Reminders. I want to build this application in
a way that it is agnostic to the actual backend. Meaning you need to have an
abstract class with the interfaces to enable all of the functionalities and
features outlined in this document that we need. The concrete implementation
should be an adapter to the Reminder CLI and needs to implement all of
these functions. In order to test this application well, create a mock
backend task management and use that always. Never communicate directly with
the Reminder CLI. Always assume that the list that you're working on is
called "develop". in addition always use a second list called "develop2"

Keep a checklist of what you did and what your status is. So next time we can continue where we left of

### Features that I need

- [x] Integrate swift adapter to make this app work with apple reminders.
      See https://github.com/florianbellmann/reminders-cli.git
      The adapter will build to a binary executable. the app should be able to talk to that binary
      Dont try to build the reminders cli. Just read the swift source code to understand how it works
- [x] Adding a task by title
- [x] Completing a task
- [x] Switching between lists
- [x] Edit dates
- [x] Move to tomorrow
- [x] Edit full card form
- [x] Edit descriptions
- [x] Edit tags
- [x] Edit prios
- [x] Edit flags
- [x] Refresh list
- [x] Handling of all tasks, not only overdue
- [x] Sorting / filtering
- [x] Async task handling with busy spinners, maybe add command queue
- [x] Fix help pages initial app functionalities
- [x] Display of further infos: Tags, recurring, flags, prios, ...
- [x] Github actions, building, tests and linting
- [x] Input hardening
- [x] Implement app logging for debugging
- [x] default list should be the first in the list. not an extra env var
- [x] handle selction and highlighhting the same
- [x] change keybindings update help pages
- [x] fix tests
- [x] task completion is not working
- [x] when switching lists, the selected index should always be reset to 1. meaning the first item in a list. this is also needed for switching to and
from the all items view. fix this and cover it with tests
- [x] i need to be able to move tasks to other lists. implement this feature with the hotkey y to choose a list to move to. cover it with tests
- [x] instead of using PYTEST_CURRENT_TEST env var. use logging.debug and enable that for the tests
- [x] testing and bug fixes
  - [x] when staring the app, i want to start in the all view. fix this and cover it with a test
  - [x] when adding an item while all view is focussed, add it to the first list in the env var. meaning the default list. fix this and cover it with a test
  - [x] i need a hotkey for adding due date today. fix this and cover it with a test
  - [x] use single line input for title. hotkey also missing
  - [x] hotkey t m and w only work while focussing a list and not in all view. but i need them to work in both. fix this and cover it with a test
  - [x] i need to be able to add and edit multiline descriptions. fix this and cover it with a test
  - [x] ctrl o does something. but how do i actually choose a sort type and direction? meaning alphabeticcal or due date. fix this and cover it with a test
  - [x] editing the date with d breaks the app. fix this and cover it with a test
  - [x] the lists are getting parsed with spaces. even some tests assert that. i want to test with spaces, but should get parsed to trimmed strings
  - [x] A does not add the today as due date. only normal creation. it should add something for today though. fix this and cover it with a test
  - [x] in the sort direction view i cant use vim keydings. change this to a popup. fix this and cover it with a test
  - [x] toggle sort direction key binding c-i does not work. fix this and cover it with a test
  - [x] no keyboard movement in date picker
- [x] use nvim for desc
- [x] I cant config desc editing with tab enter
- [x] change description editing to be a popup
- [x] change title editing to be a popup
- [x] use red, green, yellow from https://github.com/charles-001/dolphie/blob/main/dolphie/Dolphie.tcss to highlight different texts
- [x] remove vertical space betwen list items
- [ ] show tags in the list view. cover it with a test
- [x] add time stamp to logs
- [ ] recurring tasks handling
- [ ] i need to be able to create a new task zhrough a singular prompt. mesning running a quick cli prompt for getting the title and confirming the creation. then the process stops. this should be independent from the normal main application. recurring tasks loading indicators


## reminders cli

See ./reminders-cli-interface.md

### Example repos that I like

- Lazygit
- Lazydocker

### learnings about textual

- **Textual Async Testing:**
  - Use `App.run_test()` for headless execution and to get a `Pilot` object.
  - The `Pilot` object is crucial for simulating user interactions (e.g., `pilot.press()`, `pilot.click()`).
  - Tests involving Textual applications should be `async` and use `pytest-asyncio`.
  - Assertions verify the application's state after interactions.
  - Avoid directly calling app methods that modify UI state; instead, simulate user input via the `Pilot` to trigger those changes.
  - `ListView.index = None` is used to clear the highlight, as `clear_highlight()` is not a public method.
  - When a screen is dismissed, the result is passed to the `dismiss` method, and it can be accessed via `screen.result` if the screen is defined with a return type.
