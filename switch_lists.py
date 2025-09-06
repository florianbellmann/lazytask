import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager

async def main():
    task_manager = MockTaskManager()
    
    print("Getting available lists...")
    lists = await task_manager.get_lists()
    print(f"Available lists: {lists}")

    print("\nAdding a task to 'personal' list...")
    personal_task = await task_manager.add_task("Call mom", list_name="personal")
    print(f"Added task: {personal_task.title} (ID: {personal_task.id}) to list: personal")

    print("\nAdding a task to 'work' list...")
    work_task = await task_manager.add_task("Prepare presentation", list_name="work")
    print(f"Added task: {work_task.title} (ID: {work_task.id}) to list: work")

    print("\nGetting available lists again...")
    lists = await task_manager.get_lists()
    print(f"Available lists: {lists}")

    print("\nTasks in 'develop' list:")
    develop_tasks = await task_manager.get_tasks(list_name="develop")
    if develop_tasks:
        for task in develop_tasks:
            print(f"- {task.title}")
    else:
        print("No tasks in 'develop' list.")

    print("\nTasks in 'personal' list:")
    personal_tasks = await task_manager.get_tasks(list_name="personal")
    if personal_tasks:
        for task in personal_tasks:
            print(f"- {task.title}")
    else:
        print("No tasks in 'personal' list.")

    print("\nTasks in 'work' list:")
    work_tasks = await task_manager.get_tasks(list_name="work")
    if work_tasks:
        for task in work_tasks:
            print(f"- {task.title}")
    else:
        print("No tasks in 'work' list.")

if __name__ == "__main__":
    asyncio.run(main())
