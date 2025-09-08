from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container

class HelpScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(name="Help")
        yield Container(
            Static("Key Bindings:"),
            Static("r - Refresh"),
            Static("d - Details"),
            Static("e - Edit"),
            Static("t - Tomorrow"),
            Static("f - Flag"),
            Static("o - Overdue"),
            Static("s p - Sort by Priority"),
            Static("s d - Sort by Due Date"),
            Static("s c - Clear Sort"),
            Static("? - Help"),
        )
        yield Footer()
