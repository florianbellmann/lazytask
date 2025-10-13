from dataclasses import asdict, dataclass
from typing import Dict


@dataclass(frozen=True)
class Palette:
    app_background: str
    list_panel_background: str
    detail_panel_background: str
    panel_border: str
    highlight_background: str
    header_background: str
    header_text: str
    header_title: str
    header_clock: str
    footer_background: str
    footer_text: str
    tab_background: str
    tab_border: str
    tab_active_background: str
    tab_active_text: str
    tab_inactive_text: str
    list_item_border: str
    modal_background: str
    modal_border: str
    input_background: str
    input_border: str
    input_focus_border: str
    button_background: str
    button_text: str
    button_primary_background: str
    button_primary_text: str
    scrollbar_track: str
    scrollbar_thumb: str
    scrollbar_thumb_hover: str
    scrollbar_thumb_active: str
    text_primary: str
    text_secondary: str
    text_muted: str
    text_inverted: str
    accent_primary: str
    accent_secondary: str
    success: str
    warning: str
    danger: str

    def as_dict(self) -> Dict[str, str]:
        return asdict(self)


KANAGAWA = Palette(
    app_background="#1f1f28",
    list_panel_background="#16161d",
    detail_panel_background="#1f1f28",
    panel_border="#2a2a37",
    highlight_background="#2a2a37",
    header_background="#2a2a37",
    header_text="#dcd7ba",
    header_title="#9cabca",
    header_clock="#7e9cd8",
    footer_background="#2a2a37",
    footer_text="#7e9cd8",
    tab_background="#16161d",
    tab_border="#2a2a37",
    tab_active_background="#7e9cd8",
    tab_active_text="#1f1f28",
    tab_inactive_text="#9cabca",
    list_item_border="#2a2a37",
    modal_background="#1f1f28",
    modal_border="#2a2a37",
    input_background="#16161d",
    input_border="#2a2a37",
    input_focus_border="#7e9cd8",
    button_background="#16161d",
    button_text="#dcd7ba",
    button_primary_background="#7e9cd8",
    button_primary_text="#1f1f28",
    scrollbar_track="#16161d",
    scrollbar_thumb="#2a2a37",
    scrollbar_thumb_hover="#363646",
    scrollbar_thumb_active="#54546d",
    text_primary="#dcd7ba",
    text_secondary="#c8c093",
    text_muted="#938aa9",
    text_inverted="#1f1f28",
    accent_primary="#7e9cd8",
    accent_secondary="#9cabca",
    success="#a7c080",
    warning="#e6c384",
    danger="#ff5d62",
)


def get_palette() -> Palette:
    return KANAGAWA
