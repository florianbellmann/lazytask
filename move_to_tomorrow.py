import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager
import datetime

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to move to tomorrow...")
    task_to_move = await task_manager.add_task("Prepare for meeting", list_name="develop")
    print(f"Added task: {task_to_move.title} (ID: {task_to_move.id})")

    print(f"\nTask before moving: Due Date: {task_to_move.due_date}")

    print(f"\nMoving task to tomorrow...")
    moved_task = await task_manager.move_task_to_tomorrow(task_to_move.id, list_name="develop")
    
    if moved_task:
        print(f"Task moved: {moved_task.title} (New Due Date: {moved_task.due_date})")
    else:
        print("Failed to move task to tomorrow.")

    print("\nVerifying task date after move:")
    tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    found_task = next((t for t in tasks if t.id == task_to_move.id), None)
    if found_task:
        print(f"- {found_task.title} (Due Date: {found_task.due_date})")
    else:
        print("Task not found after move.")

if __name__ == "__main__":
    asyncio.run(main())
