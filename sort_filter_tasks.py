import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager
import datetime

async def main():
    task_manager = MockTaskManager()
    
    print("Adding some tasks for sorting and filtering...")
    # Task C (High Priority)
    task_c = await task_manager.add_task("Task C (High Priority)", list_name="develop")
    await task_manager.edit_task_priority(task_c.id, 1, list_name="develop")

    # Task A (Low Priority)
    task_a = await task_manager.add_task("Task A (Low Priority)", list_name="develop")
    await task_manager.edit_task_priority(task_a.id, 3, list_name="develop")

    # Task B (Medium Priority, Completed)
    task_b = await task_manager.add_task("Task B (Medium Priority, Completed)", list_name="develop")
    await task_manager.edit_task_priority(task_b.id, 2, list_name="develop")
    await task_manager.complete_task(task_b.id, list_name="develop")

    # Task D (No Priority, Due Tomorrow)
    task_d = await task_manager.add_task("Task D (No Priority, Due Tomorrow)", list_name="develop")
    await task_manager.edit_task_date(task_d.id, (datetime.date.today() + datetime.timedelta(days=1)).isoformat(), list_name="develop")

    # Task E (High Priority, Tagged)
    task_e = await task_manager.add_task("Task E (High Priority, Tagged)", list_name="develop")
    await task_manager.edit_task_priority(task_e.id, 1, list_name="develop")
    await task_manager.edit_task_tags(task_e.id, ["urgent", "work"], list_name="develop")

    print("\nAll tasks (unsorted, unfiltered):")
    all_tasks = await task_manager.get_tasks(list_name="develop", include_completed=True)
    for task in all_tasks:
        print(f"- {task.title} (Prio: {task.priority}, Due: {task.due_date}, Completed: {task.completed}, Tags: {task.tags})")

    print("\nSorting tasks by priority (ascending)...")
    sorted_by_priority = await task_manager.sort_tasks(list_name="develop", sort_by="priority")
    for task in sorted_by_priority:
        print(f"- {task.title} (Prio: {task.priority})")

    print("\nSorting tasks by due date (ascending)...")
    sorted_by_date = await task_manager.sort_tasks(list_name="develop", sort_by="due_date")
    for task in sorted_by_date:
        print(f"- {task.title} (Due: {task.due_date})")

    print("\nFiltering tasks by query 'Task C'...")
    filtered_by_query = await task_manager.filter_tasks(list_name="develop", query="Task C")
    for task in filtered_by_query:
        print(f"- {task.title}")

    print("\nFiltering tasks by priority 1 (High Priority)...")
    filtered_by_priority = await task_manager.filter_tasks(list_name="develop", priority=1)
    for task in filtered_by_priority:
        print(f"- {task.title} (Prio: {task.priority})")

    print("\nFiltering tasks by tags 'urgent'...")
    filtered_by_tags = await task_manager.filter_tasks(list_name="develop", tags=["urgent"])
    for task in filtered_by_tags:
        print(f"- {task.title} (Tags: {task.tags})")

    print("\nFiltering tasks by completed status (only completed)...")
    filtered_completed = await task_manager.filter_tasks(list_name="develop", include_completed=True)
    for task in filtered_completed:
        if task.completed:
            print(f"- {task.title} (Completed: {task.completed})")

if __name__ == "__main__":
    asyncio.run(main())