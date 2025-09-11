# Reminders CLI Interface

This document outlines the command-line interface for the `reminders-cli` tool.

## Usage

The basic command structure is:

```bash
reminders [command] [arguments] [options]
```

## Commands

### `show-lists`

Prints the names of all available reminder lists.

**Options:**

*   `--format <format>`: Specify the output format. Can be `plain` (default) or `json`.

### `show-all`

Prints all reminders from all lists.

**Options:**

*   `--only-completed`: Show only completed reminders.
*   `--include-completed`: Include completed reminders in the output.
*   `--due-date <date>`: Show only reminders due on a specific date.
*   `--format <format>`: Specify the output format. Can be `plain` (default) or `json`.

### `show`

Prints the reminders on a specific list.

**Arguments:**

*   `listName`: The name of the list to show reminders from.

**Options:**

*   `--only-completed`: Show only completed reminders.
*   `--include-completed`: Include completed reminders in the output.
*   `--sort <sort>`: Sort the reminders by a specific criteria. Available options: `none` (default), `name`, `due-date`, `creation-date`, `priority`.
*   `--sort-order <order>`: Specify the sort order. Available options: `ascending` (default), `descending`.
*   `--due-date <date>`: Show only reminders due on a specific date.
*   `--format <format>`: Specify the output format. Can be `plain` (default) or `json`.

### `add`

Adds a new reminder to a list.

**Arguments:**

*   `listName`: The name of the list to add the reminder to.
*   `reminder`: The content of the reminder.

**Options:**

*   `--due-date <date>`: The date the reminder is due.
*   `--priority <priority>`: The priority of the reminder. Available options: `none` (default), `low`, `medium`, `high`.
*   `--notes <notes>`: Add notes to the reminder.
*   `--format <format>`: Specify the output format. Can be `plain` (default) or `json`.

### `complete`

Marks a reminder as completed.

**Arguments:**

*   `listName`: The name of the list the reminder is on.
*   `index`: The index or ID of the reminder to complete.

### `uncomplete`

Marks a reminder as not completed.

**Arguments:**

*   `listName`: The name of the list the reminder is on.
*   `index`: The index or ID of the reminder to uncomplete.

### `delete`

Deletes a reminder.

**Arguments:**

*   `listName`: The name of the list the reminder is on.
*   `index`: The index or ID of the reminder to delete.

### `edit`

Edits the text or notes of a reminder.

**Arguments:**

*   `listName`: The name of the list the reminder is on.
*   `index`: The index or ID of the reminder to edit.
*   `reminder`: The new content of the reminder.

**Options:**

*   `--notes <notes>`: The new notes for the reminder.

### `new-list`

Creates a new reminder list.

**Arguments:**

*   `listName`: The name of the new list.

**Options:**

*   `--source <source>`: The source of the list.
