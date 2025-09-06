import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Adding a task to complete...")
    task_to_complete = await task_manager.add_task("Finish report", list_name="develop")
    print(f"Added task: {task_to_complete.title} (ID: {task_to_complete.id})")

    print("\nTasks before completion:")
    tasks_before = await task_manager.get_tasks(list_name="develop")
    for task in tasks_before:
        print(f"- {task.title} (Completed: {task.completed})")

    print(f"\nCompleting task: {task_to_complete.title}...")
    completed_task = await task_manager.complete_task(task_to_complete.id, list_name="develop")
    if completed_task:
        print(f"Task completed: {completed_task.title} (Completed: {completed_task.completed})")
    else:
        print("Failed to complete task.")

    print("\nTasks after completion (excluding completed by default):")
    tasks_after = await task_manager.get_tasks(list_name="develop")
    if tasks_after:
        for task in tasks_after:
            print(f"- {task.title} (Completed: {task.completed})")
    else:
        print("No active tasks found.")

    print("\nTasks after completion (including completed):")
    all_tasks_after = await task_manager.get_tasks(list_name="develop", include_completed=True)
    for task in all_tasks_after:
        print(f"- {task.title} (Completed: {task.completed})")

if __name__ == "__main__":
    asyncio.run(main())
