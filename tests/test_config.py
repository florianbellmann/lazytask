import os
import pytest
from lazytask.presentation.app import LazyTaskApp


def test_default_list_from_env_var(monkeypatch):
    """Test that the default list is read from the environment variable."""
    monkeypatch.setenv("LAZYTASK_LISTS", "my-test-list,another-list")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "my-test-list")
    app = LazyTaskApp()
    assert app.current_list == "my-test-list"


def test_default_list_fallback():
    """Test that the default list falls back to 'develop'."""
    # Make sure the env var is not set
    if "LAZYTASK_DEFAULT_LIST" in os.environ:
        del os.environ["LAZYTASK_DEFAULT_LIST"]
    if "LAZYTASK_LISTS" in os.environ:
        del os.environ["LAZYTASK_LISTS"]
    app = LazyTaskApp()
    assert app.current_list == "develop"


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
    monkeypatch.setenv("LAZYTASK_LISTS", "work,home,personal")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "home")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        list_tabs = pilot.app.query_one("ListTabs")
        assert list_tabs.children[0].label == "work"
        assert list_tabs.children[1].label == "home"
        assert list_tabs.children[2].label == "personal"
        assert list_tabs.active == "home"


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


# in dev always use develop and develop2
# in testing use test and test2
