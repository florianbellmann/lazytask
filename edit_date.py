import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager
import datetime

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to edit its date...")
    task_to_edit = await task_manager.add_task("Submit expense report", list_name="develop")
    print(f"Added task: {task_to_edit.title} (ID: {task_to_edit.id})")

    print(f"\nTask before date edit: Due Date: {task_to_edit.due_date}")

    new_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat() # One week from now
    print(f"\nEditing task date to: {new_date}...")
    edited_task = await task_manager.edit_task_date(task_to_edit.id, new_date, list_name="develop")
    
    if edited_task:
        print(f"Task date edited: {edited_task.title} (New Due Date: {edited_task.due_date})")
    else:
        print("Failed to edit task date.")

    print("\nVerifying task date after edit:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Due Date: {found_task.due_date})")
    else:
        print("Task not found after edit.")

if __name__ == "__main__":
    asyncio.run(main())
