# LazyTask Helper Guide

## Build Commands
- Build project: `./build` (builds reminders adapter if needed)
- Run project: `.build/lazytask`
- Test single file: `go test -v ./infrastructure/reminders_task_controller_test.go`
- Run all tests: `go test ./...`
- Go linting: `golangci-lint run`

## Code Style
- Imports: Standard Go groups (stdlib, external, internal) with alphabetical ordering
- Naming: camelCase for vars/fields, PascalCase for exported functions/structs
- Error handling: Return errors with context, check errors immediately
- Domain-driven design: Keep domain logic in domain/, infrastructure in infrastructure/
- UI components: Use Bubbletea framework patterns with models implementing tea.Model
- File organization: Group related functionality in packages
- Tests: Test files alongside source code with _test.go suffix
- Comments: Document exported functions with proper Go doc comments

## Project Structure
- Go application using Bubbletea for TUI
- Swift adapter for Apple Reminders integration
- Follows domain-driven design principles