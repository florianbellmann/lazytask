from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container
from lazytask.infrastructure.mock_task_manager import MockTaskManager
import asyncio

class LazyTaskApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, task_manager: MockTaskManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_manager = task_manager
        self.tasks_display = Static("Loading tasks...", id="tasks_display")

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Button("Refresh Tasks", id="refresh_button")
            yield self.tasks_display
        yield Footer()

    async def on_mount(self) -> None:
        await self.action_refresh_tasks()

    async def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    async def action_quit(self) -> None:
        self.exit()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh_button":
            await self.action_refresh_tasks()

    async def action_refresh_tasks(self) -> None:
        self.tasks_display.update("Refreshing tasks...")
        tasks = await self.task_manager.get_tasks(list_name="develop")
        
        if tasks:
            task_list_str = "\n".join([f"- {task.title} (ID: {task.id}, Completed: {task.completed})" for task in tasks])
            self.tasks_display.update(f"Tasks in 'develop' list:\n{task_list_str}")
        else:
            self.tasks_display.update("No tasks in 'develop' list.")

if __name__ == "__main__":
    task_manager_instance = MockTaskManager()
    app = LazyTaskApp(task_manager=task_manager_instance)
    app.run()
