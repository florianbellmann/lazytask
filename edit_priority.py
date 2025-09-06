import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to edit its priority...")
    task_to_edit = await task_manager.add_task("Review pull request", list_name="develop")
    print(f"Added task: {task_to_edit.title} (ID: {task_to_edit.id})")

    print(f"\nTask before priority edit: Priority: {task_to_edit.priority}")

    new_priority = 1 # High priority
    print(f"\nEditing task priority to: {new_priority}...")
    edited_task = await task_manager.edit_task_priority(task_to_edit.id, new_priority, list_name="develop")
    
    if edited_task:
        print(f"Task priority edited: {edited_task.title} (New Priority: {edited_task.priority})")
    else:
        print("Failed to edit task priority.")

    print("\nVerifying task priority after edit:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Priority: {found_task.priority})")
    else:
        print("Task not found after edit.")

if __name__ == "__main__":
    asyncio.run(main())
