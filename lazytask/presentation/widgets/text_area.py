from textual.widgets import TextArea as _TextualTextArea


class TextArea(_TextualTextArea):
    """Custom TextArea wrapper to provide a stable import path."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
