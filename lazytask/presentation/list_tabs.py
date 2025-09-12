from textual.widgets import Static
from rich.text import Text
from typing import List

class ListTabs(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tabs = Text()

    def update_lists(self, lists: List[str], current_list: str):
        tabs = Text.from_markup(" | ".join(
            f"[bold reverse] {lst} [/]" if lst == current_list else f" {lst} "
            for lst in ["all"] + lists
        ))
        self.tabs = tabs
        self.update(self.tabs)
