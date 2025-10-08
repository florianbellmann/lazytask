from dataclasses import dataclass
from typing import cast

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView


@dataclass(frozen=True)
class SortOption:
    label: str
    sort_by: str
    reverse: bool


SORT_OPTIONS: list[SortOption] = [
    SortOption(label="Due date ↑", sort_by="due_date", reverse=False),
    SortOption(label="Due date ↓", sort_by="due_date", reverse=True),
    SortOption(label="Title ↑", sort_by="title", reverse=False),
    SortOption(label="Title ↓", sort_by="title", reverse=True),
    SortOption(label="Creation date ↑", sort_by="creation_date", reverse=False),
    SortOption(label="Creation date ↓", sort_by="creation_date", reverse=True),
]


class SortOptionListItem(ListItem):
    def __init__(self, option: SortOption):
        super().__init__(Label(option.label))
        self.option = option


class SortOptionsScreen(ModalScreen[tuple[str, bool] | None]):
    DEFAULT_CSS = """
    SortOptionsScreen > Center {
        align: center middle;
    }

    SortOptionsScreen #sort_options_popup {
        width: 48;
        min-width: 42;
        border: round $accent;
        padding: 1 2;
        background: $panel;
    }

    SortOptionsScreen #sort_options_title {
        text-style: bold;
    }

    SortOptionsScreen ListView#sort_options_list {
        height: auto;
    }
    """

    def __init__(self, current_sort: str, current_reverse: bool):
        super().__init__()
        self.current_sort = current_sort
        self.current_reverse = current_reverse

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="sort_options_popup"):
                yield Label("Select sort field & direction", id="sort_options_title")
                yield ListView(
                    *[SortOptionListItem(option) for option in SORT_OPTIONS],
                    id="sort_options_list",
                )

    def on_mount(self) -> None:
        sort_list_view = self._list_view()
        for index, option in enumerate(SORT_OPTIONS):
            if (
                option.sort_by == self.current_sort
                and option.reverse == self.current_reverse
            ):
                sort_list_view.index = index
                break
        else:
            sort_list_view.index = 0
        sort_list_view.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        option = cast(SortOptionListItem, event.item).option
        self.dismiss((option.sort_by, option.reverse))

    def on_key(self, event: Key) -> None:
        list_view = self._list_view()

        if event.key in {"j", "down"}:
            event.stop()
            list_view.action_cursor_down()
            return

        if event.key in {"k", "up"}:
            event.stop()
            list_view.action_cursor_up()
            return

        if event.key == "g":
            event.stop()
            if list_view.children:
                list_view.index = 0
            return

        if event.key == "G":
            event.stop()
            if list_view.children:
                list_view.index = len(list_view.children) - 1
            return

        if event.key == "escape":
            event.stop()
            self.dismiss(None)

    def _list_view(self) -> ListView:
        return self.query_one("#sort_options_list", ListView)
