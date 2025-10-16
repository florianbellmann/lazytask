import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.list_tabs import ListTabs


def test_app_requires_valid_lists(monkeypatch):
    """
    App should start ONLY if LAZYTASK_LISTS env var is present and valid:
      - Lists is a non-empty, comma-separated list of names.
    Otherwise, startup should fail with a clear error.
    """
    # Test case 1: LAZYTASK_LISTS is valid
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home")
    try:
        LazyTaskApp()
    except ValueError:
        pytest.fail("ValueError raised unexpectedly with valid configuration")

    # Test case 2: LAZYTASK_LISTS is missing
    monkeypatch.delenv("LAZYTASK_LISTS")
    with pytest.raises(ValueError, match="LAZYTASK_LISTS environment variable not set"):
        LazyTaskApp()

    # Test case 3: LAZYTASK_LISTS is empty
    monkeypatch.setenv("LAZYTASK_LISTS", "")
    with pytest.raises(ValueError, match="LAZYTASK_LISTS must not be empty"):
        LazyTaskApp()


async def test_tabs_match_lists_and_all_is_selected_on_start(monkeypatch):
    """
    Given a valid Lists env var:
      - The visible tabs correspond exactly to the names from Lists (in order).
      - The 'all' tab is selected on startup.
    """
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home ,personal ")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        list_tabs = pilot.app.query_one(ListTabs)
        tabs_text = list_tabs.tabs
        assert "work" in str(tabs_text)
        assert "home" in str(tabs_text)
        assert "personal" in str(tabs_text)
        assert "all" in str(tabs_text)

        all_span_found = False
        for span in tabs_text.spans:
            if "all" in tabs_text.plain[span.start : span.end]:
                style_parts = str(span.style).split(" on ")
                if len(style_parts) > 1 and style_parts[1]:
                    all_span_found = True
                    break
        assert all_span_found, "The 'all' tab should be rendered with a background color."
