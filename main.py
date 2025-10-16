import argparse
import asyncio
import json
from typing import Any

from textual.widgets import Label, ListView

from lazytask.presentation.app import LazyTaskApp, TaskListItem


def capture_list_snapshot() -> list[dict[str, Any]]:
    """Render the app headlessly and capture styling details for each list entry."""

    async def _capture_snapshot(app: LazyTaskApp) -> list[dict[str, Any]]:
        async with app.run_test() as pilot:
            await pilot.pause()
            tasks_list = app.query_one(ListView)
            snapshot: list[dict[str, Any]] = []
            for index, child in enumerate(tasks_list.children):
                if isinstance(child, TaskListItem):
                    title_label = child.query_one("#task-title", expect_type=Label)
                    due_label = child.query_one("#task-due-date", expect_type=Label)
                    snapshot.append(
                        {
                            "index": index,
                            "task_id": child.data.id,
                            "title": child.data.title,
                            "title_color": str(title_label.styles.color),
                            "title_plain_text": str(
                                getattr(title_label.renderable, "plain", "")
                            ),
                            "due_text": str(
                                getattr(due_label.renderable, "plain", "")
                            ),
                            "due_color": str(due_label.styles.color),
                            "item_classes": sorted(child.classes),
                        }
                    )
            return snapshot

    app = LazyTaskApp()
    return asyncio.run(_capture_snapshot(app))


def main():
    parser = argparse.ArgumentParser(description="LazyTask CLI entry point.")
    parser.add_argument(
        "--debug-list-snapshot",
        action="store_true",
        help="Render the list view headlessly and dump styling diagnostics as JSON.",
    )
    args = parser.parse_args()

    if args.debug_list_snapshot:
        try:
            snapshot = capture_list_snapshot()
        except Exception as exc:
            raise SystemExit(f"Failed to capture list snapshot: {exc}") from exc
        print(json.dumps(snapshot, indent=2))
        return

    app = LazyTaskApp()
    app.run()


if __name__ == "__main__":
    main()
