# Developer Guide

This document provides a developer-focused overview of the LazyTask application's architecture, core concepts, and implementation details.

## 1. Overall Architecture

LazyTask is a task management application for the terminal, built with Python and the [Textual](https://textual.textualize.io/) framework. It follows a Domain-Driven Design (DDD) approach, separating the application into distinct layers:

-   **Domain:** Contains the core business logic and data models of the application. This layer is independent of any specific framework or technology.
-   **Application:** Orchestrates the domain logic by defining use cases that represent user actions.
-   **Infrastructure:** Provides concrete implementations of the interfaces defined in the domain layer. This includes data persistence, external service integrations, etc.
-   **Presentation:** The user interface (UI) layer, built with Textual. It interacts with the application layer to execute use cases and display data to the user.

This layered architecture promotes separation of concerns, making the application more modular, testable, and maintainable.

## 2. Core Concepts

### 2.1. Domain

The domain layer is the heart of the application and consists of the following key components:

-   **`Task` (`lazytask/domain/task.py`):** A dataclass representing a single task with its attributes (ID, title, due date, etc.).
-   **`TaskManager` (`lazytask/domain/task_manager.py`):** An abstract base class (ABC) that defines the contract for managing tasks. It includes methods for adding, completing, retrieving, and editing tasks. This interface-based approach allows for different backend implementations (e.g., a mock backend for testing, a backend that interacts with Apple Reminders).

### 2.2. Application

The application layer contains use cases that encapsulate specific user actions. Each use case class has an `execute` method that orchestrates the necessary steps to perform the action.

-   **Use Cases (`lazytask/application/use_cases.py`):**
    -   `AddTask`: Adds a new task.
    -   `GetTasks`: Retrieves a list of tasks.
    -   `CompleteTask`: Marks a task as complete.
    -   `UpdateTask`: Modifies an existing task.
    -   `GetLists`: Retrieves the available task lists.

These use cases depend on the `TaskManager` interface, not on a concrete implementation.

### 2.3. Infrastructure

The infrastructure layer provides the concrete implementations of the domain interfaces.

-   **`MockTaskManager` (`lazytask/infrastructure/mock_task_manager.py`):** A mock implementation of the `TaskManager` that stores tasks in a JSON file (`mock_tasks.json`). This is used for development and testing, allowing the application to be run without a real backend.
-   **`RemindersCliTaskManager` (`lazytask/infrastructure/reminders_cli_task_manager.py`):** An implementation of the `TaskManager` that interacts with the Apple Reminders application through the `reminders-cli` command-line tool.

### 2.4. Presentation (UI)

The presentation layer is responsible for the user interface, built with the Textual framework.

-   **`LazyTaskApp` (`lazytask/presentation/app.py`):** The main Textual application class. It handles user input, displays tasks, and interacts with the application layer's use cases to perform actions.
-   **Screens (`lazytask/presentation/*.py`):** The application uses various screens for different UI functionalities:
    -   `EditScreen`: A screen for editing the details of a task.
    -   `HelpScreen`: Displays a list of available keybindings.
    -   `DatePickerScreen`: A screen for selecting a date.
    -   `TextInputModal`: A modal dialog for entering text.
-   **Widgets (`lazytask/presentation/*.py`):**
    -   `TaskListItem`: A custom `ListItem` widget to display a single task in the `ListView`.
    -   `TaskDetail`: A widget to display the details of the selected task.
    -   `ListTabs`: A widget to display and switch between task lists.

## 3. Dependency Injection

The application uses a simple dependency injection container to manage the dependencies between the different layers.

-   **`DependencyContainer` (`lazytask/container.py`):** This class is responsible for creating and providing instances of the use cases and the `TaskManager`. By default, it's configured to use the `MockTaskManager`. The `set_task_manager` method allows switching to a different `TaskManager` implementation (e.g., `RemindersCliTaskManager`).

This approach decouples the application components and makes it easy to swap out implementations, which is particularly useful for testing.

## 4. Testing

The project includes a suite of tests in the `tests/` directory. The tests are written using `pytest` and `pytest-asyncio` for testing asynchronous code.

To run the tests, execute the following command:

```bash
uv run pytest
```

The tests cover various aspects of the application, including:

-   **Application Logic:** Testing the use cases with the mock task manager.
-   **UI Interactions:** Using Textual's `run_test` method to simulate user interactions and assert the application's state.
-   **Configuration and Edge Cases:** Testing different configurations and handling of edge cases.

## 5. Getting Started

1.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

2.  **Set Environment Variables:**
    Create a `.env` file in the root of the project and add the following environment variable:
    ```
    LAZYTASK_LISTS=develop,develop2
    ```

3.  **Run the Application:**
    ```bash
    uv run python -m lazytask
    ```

This will start the LazyTask application in your terminal, using the `MockTaskManager` by default.
