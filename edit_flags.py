import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to edit its flag...")
    task_to_edit = await task_manager.add_task("Follow up with client", list_name="develop")
    print(f"Added task: {task_to_edit.title} (ID: {task_to_edit.id})")

    print(f"\nTask before flag edit: Flagged: {task_to_edit.flagged}")

    new_flag_status = True # Set flag
    print(f"\nEditing task flag to: {new_flag_status}...")
    edited_task = await task_manager.edit_task_flag(task_to_edit.id, new_flag_status, list_name="develop")
    
    if edited_task:
        print(f"Task flag edited: {edited_task.title} (New Flagged Status: {edited_task.flagged})")
    else:
        print("Failed to edit task flag.")

    print("\nVerifying task flag after edit:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Flagged: {found_task.flagged})")
    else:
        print("Task not found after edit.")

    # Now, unflag the task
    new_flag_status = False # Unset flag
    print(f"\nEditing task flag to: {new_flag_status} (unflagging)...")
    edited_task = await task_manager.edit_task_flag(task_to_edit.id, new_flag_status, list_name="develop")
    
    if edited_task:
        print(f"Task flag edited: {edited_task.title} (New Flagged Status: {edited_task.flagged})")
    else:
        print("Failed to unflag task.")

    print("\nVerifying task flag after unflagging:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_edit.id), None)
    if found_task:
        print(f"- {found_task.title} (Flagged: {found_task.flagged})")
    else:
        print("Task not found after unflagging.")

if __name__ == "__main__":
    asyncio.run(main())
