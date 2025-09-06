import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a new task...")
    new_task = await task_manager.add_task("Buy milk", list_name="develop")
    print(f"Added task: {new_task.title} (ID: {new_task.id})")

    print("\nGetting all tasks in 'develop' list...")
    tasks = await task_manager.get_tasks(list_name="develop")
    if tasks:
        for task in tasks:
            print(f"- {task.title} (Completed: {task.completed})")
    else:
        print("No tasks found.")

if __name__ == "__main__":
    asyncio.run(main())
