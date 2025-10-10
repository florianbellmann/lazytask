from textual.widgets import Static
from rich.text import Text
from typing import List


class ListTabs(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tabs = Text()

    def update_lists(self, lists: List[str], current_list: str):
        normalized_lists = ["all"] + [name for name in lists if name != "all"]
        tab_segments = []
        for name in normalized_lists:
            if name == current_list:
                tab_segments.append(f"[#0a0e1b on #8fb0ee] {name} [/]")
            else:
                tab_segments.append(f"[#8fb0ee]{name}[/]")
        self.tabs = Text.from_markup("   ".join(tab_segments))
        self.update(self.tabs)
