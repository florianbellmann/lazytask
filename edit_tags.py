import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to edit its tags...")
    task_to_edit = await task_manager.add_task("Research new framework", list_name="develop")
    print(f"Added task: {task_to_edit.title} (ID: {task_to_edit.id})")

    print(f"\nTask before tags edit: Tags: {task_to_edit.tags}")

    new_tags = ["python", "backend", "learning"]
    print(f"\nEditing task tags to: {new_tags}...")
    edited_task = await task_manager.edit_task_tags(task_to_edit.id, new_tags, list_name="develop")
    
    if edited_task:
        print(f"Task tags edited: {edited_task.title} (New Tags: {edited_task.tags})")
    else:
        print("Failed to edit task tags.")

    print("\nVerifying task tags after edit:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Tags: {found_task.tags})")
    else:
        print("Task not found after edit.")

if __name__ == "__main__":
    asyncio.run(main())
