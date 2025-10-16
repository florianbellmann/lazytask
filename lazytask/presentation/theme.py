from __future__ import annotations

from textwrap import dedent

from lazytask.presentation.palette import Palette, get_palette


THEME_TEMPLATE = """
* {{
    color: {text_primary};
    scrollbar-background: {scrollbar_track};
    scrollbar-background-hover: {scrollbar_track};
    scrollbar-background-active: {scrollbar_track};
    scrollbar-color: {scrollbar_thumb};
    scrollbar-color-hover: {scrollbar_thumb_hover};
    scrollbar-color-active: {scrollbar_thumb_active};
}}

LazyTaskApp, Screen {{
    background: {app_background};
}}

Header {{
    background: {header_background};
    color: {header_text};
    text-style: bold;
    content-align: center middle;
    padding: 0 1;
    height: 1;
}}

Header Static#title {{
    color: {header_title};
}}

Header Static#clock {{
    color: {header_clock};
}}

Footer {{
    background: {footer_background};
    color: {footer_text};
    height: 1;
    padding: 0 1;
}}

ListTabs {{
    background: {tab_background};
    border-bottom: solid {tab_border};
    color: {tab_inactive_text};
    content-align: center middle;
    padding: 0 1;
}}

#main_layout {{
    height: 1fr;
}}

Horizontal > #tasks_panel {{
    width: 3fr;
    background: {list_panel_background};
    border-right: solid {panel_border};
}}

ListView#tasks_list {{
    background: {list_panel_background};
    padding: 0;
}}

TaskListItem {{
    background: {list_panel_background};
    border-bottom: solid {list_item_border};
    padding: 0 1;
    margin: 0;
    height: auto;
}}

TaskListItem #task-item-row {{
    width: 100%;
    height: 1;
    content-align: left middle;
}}

TaskListItem.-highlight {{
    background: {highlight_background};
}}

TaskListItem.-highlight #task-title {{
    text-style: bold;
}}

TaskListItem Label#task-title {{
    color: {text_primary};
}}

TaskListItem.completed #task-title {{
    color: {text_muted};
}}

TaskListItem Label#task-due-date {{
    width: 16;
    content-align: right middle;
    color: {accent_primary};
}}

TaskDetail {{
    width: 2fr;
    background: {detail_panel_background};
    border-left: solid {panel_border};
    padding: 1;
}}

ModalScreen {{
    background: {app_background};
}}

TextInputModal #dialog,
EditScreen #edit-task-dialog,
SelectListScreen ListView#select_list_view,
SortOptionsScreen #sort_options_popup,
HelpScreen #help-text,
DatePicker {{
    background: {modal_background};
    border: solid {modal_border};
    padding: 1;
}}

Input,
TextInputModal TextArea#input,
EditScreen TextArea,
EditScreen Input {{
    background: {input_background};
    border: solid {input_border};
    color: {text_primary};
}}

Input:focus,
TextInputModal TextArea#input:focus,
EditScreen TextArea:focus,
EditScreen Input:focus {{
    border: solid {input_focus_border};
}}

Button {{
    background: {button_background};
    border: solid transparent;
    color: {button_text};
    padding: 0 2;
}}

Button.-primary {{
    background: {button_primary_background};
    color: {button_primary_text};
}}

LoadingIndicator#tasks_loading {{
    color: {accent_primary};
    offset: 50% 50%;
    layer: overlay;
}}
"""


def build_theme_css(palette: Palette | None = None) -> str:
    selected_palette = palette or get_palette()
    css = THEME_TEMPLATE.format(**selected_palette.as_dict())
    return dedent(css).strip()
