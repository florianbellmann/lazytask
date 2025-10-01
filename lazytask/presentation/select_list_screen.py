from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label
from typing import cast


class SelectableListItem(ListItem):
    def __init__(self, name: str):
        super().__init__(Label(name))
        self.list_name = name


class SelectListScreen(ModalScreen[str]):
    def __init__(self, lists: list[str]):
        super().__init__()
        self.lists = lists

    def compose(self) -> ComposeResult:
        yield ListView(
            *[SelectableListItem(name) for name in self.lists],
            id="select_list_view",
        )

    def on_list_view_selected(self, event: ListView.Selected):
        self.dismiss(cast(SelectableListItem, event.item).list_name)
