import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding some tasks to the 'develop' list...")
    await task_manager.add_task("Task 1", list_name="develop")
    await task_manager.add_task("Task 2", list_name="develop")
    await task_manager.add_task("Task 3", list_name="develop")

    print("\nInitial tasks in 'develop' list:")
    initial_tasks = await task_manager.get_tasks(list_name="develop")
    for task in initial_tasks:
        print(f"- {task.title}")

    print("\nSimulating an external change (e.g., adding another task directly to the mock)...")
    # In a real scenario, this would be an external system adding a task
    await task_manager.add_task("Task 4 (added externally)", list_name="develop")

    print("\nRefreshing the 'develop' list...")
    refreshed_tasks = await task_manager.refresh_tasks(list_name="develop")
    
    print("\nTasks in 'develop' list after refresh:")
    if refreshed_tasks:
        for task in refreshed_tasks:
            print(f"- {task.title}")
    else:
        print("No tasks found after refresh.")

if __name__ == "__main__":
    asyncio.run(main())
