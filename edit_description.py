import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to edit its description...")
    task_to_edit = await task_manager.add_task("Write project proposal", list_name="develop")
    print(f"Added task: {task_to_edit.title} (ID: {task_to_edit.id})")

    print(f"\nTask before description edit: Description: {task_to_edit.description}")

    new_description = "Outline the key features, benefits, and timeline for the new project."
    print(f"\nEditing task description to: \"{new_description}\"...")
    edited_task = await task_manager.edit_task_description(task_to_edit.id, new_description, list_name="develop")
    
    if edited_task:
        print(f"Task description edited: {edited_task.title} (New Description: {edited_task.description})")
    else:
        print("Failed to edit task description.")

    print("\nVerifying task description after edit:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Description: {found_task.description})")
    else:
        print("Task not found after edit.")

if __name__ == "__main__":
    asyncio.run(main())
