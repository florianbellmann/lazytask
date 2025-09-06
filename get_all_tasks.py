import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding some tasks, including a completed one...")
    task1 = await task_manager.add_task("Active Task 1", list_name="develop")
    task2 = await task_manager.add_task("Completed Task 2", list_name="develop")
    await task_manager.complete_task(task2.id, list_name="develop")
    task3 = await task_manager.add_task("Active Task 3", list_name="develop")

    print("\nGetting tasks (default: excluding completed)...")
    active_tasks = await task_manager.get_tasks(list_name="develop")
    if active_tasks:
        for task in active_tasks:
            print(f"- {task.title} (Completed: {task.completed})")
    else:
        print("No active tasks found.")

    print("\nGetting all tasks (including completed)...")
    all_tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    if all_tasks:
        for task in all_tasks:
            print(f"- {task.title} (Completed: {task.completed})")
    else:
        print("No tasks found (even completed ones).")

if __name__ == "__main__":
    asyncio.run(main())
