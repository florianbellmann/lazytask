import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.list_tabs import ListTabs


def test_default_list_from_env_var(monkeypatch):
    """Test that the default list is read from the environment variable."""
    monkeypatch.setenv("LAZYTASK_LISTS", "my-test-list, another-list")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "my-test-list")
    app = LazyTaskApp()
    assert app.current_list == "my-test-list"


# ----------------------------
# Feature Tests: Configuration
# Env vars:
#   - Lists: comma-separated string of list names
#   - DefaultList: must be one of the names in Lists
# ----------------------------


def test_app_requires_valid_lists_and_defaultlist(monkeypatch):
    """
    App should start ONLY if BOTH env vars are present and valid:
      - Lists is a non-empty, comma-separated list of names.
      - DefaultList is a non-empty string and is one of Lists.
    Otherwise, startup should fail with a clear error.
    """
    # Test case 1: Both variables are valid
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "work")
    try:
        LazyTaskApp()
    except ValueError:
        pytest.fail("ValueError raised unexpectedly with valid configuration")

    # Test case 2: LAZYTASK_LISTS is missing
    monkeypatch.delenv("LAZYTASK_LISTS")
    with pytest.raises(ValueError, match="LAZYTASK_LISTS environment variable not set"):
        LazyTaskApp()

    # Test case 3: LAZYTASK_DEFAULT_LIST is missing
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home")
    monkeypatch.delenv("LAZYTASK_DEFAULT_LIST")
    with pytest.raises(
        ValueError, match="LAZYTASK_DEFAULT_LIST environment variable not set"
    ):
        LazyTaskApp()

    # Test case 4: LAZYTASK_LISTS is empty
    monkeypatch.setenv("LAZYTASK_LISTS", "")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "work")
    with pytest.raises(ValueError, match="LAZYTASK_LISTS must not be empty"):
        LazyTaskApp()

    # Test case 5: LAZYTASK_DEFAULT_LIST is not in LAZYTASK_LISTS
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "personal")
    with pytest.raises(
        ValueError,
        match="LAZYTASK_DEFAULT_LIST 'personal' not in LAZYTASK_LISTS",
    ):
        LazyTaskApp()


async def test_tabs_match_lists_and_default_selected_on_start(monkeypatch):
    """
    Given valid Lists and DefaultList:
      - The visible tabs correspond exactly to the names from Lists (in order).
      - The tab corresponding to DefaultList is selected on startup.
    """
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home ,personal ")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "home")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        list_tabs = pilot.app.query_one(ListTabs)
        tabs_text = list_tabs.tabs
        assert "work" in str(tabs_text)
        assert "home" in str(tabs_text)
        assert "personal" in str(tabs_text)

        home_span_found = False
        for span in tabs_text.spans:
            if (
                "home" in tabs_text.plain[span.start : span.end]
                and "reverse" in span.style
            ):
                home_span_found = True
                break
        assert home_span_found, "The 'home' tab should be rendered with reverse style."


def test_defaultlist_must_be_in_lists_else_error(monkeypatch):
    """
    If DefaultList is NOT one of the comma-separated entries in Lists:
      - The app should fail fast and report a helpful error.
    """
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "personal")
    with pytest.raises(
        ValueError,
        match="LAZYTASK_DEFAULT_LIST 'personal' not in LAZYTASK_LISTS",
    ):
        LazyTaskApp()
