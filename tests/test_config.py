import os
from unittest.mock import patch
import pytest
from lazytask.presentation.app import LazyTaskApp


def test_default_list_from_env_var(monkeypatch):
    """Test that the default list is read from the environment variable."""
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "my-test-list")
    app = LazyTaskApp()
    assert app.current_list == "my-test-list"


def test_default_list_fallback():
    """Test that the default list falls back to 'develop'."""
    # Make sure the env var is not set
    if "LAZYTASK_DEFAULT_LIST" in os.environ:
        del os.environ["LAZYTASK_DEFAULT_LIST"]
    app = LazyTaskApp()
    assert app.current_list == "develop"
    
    
    
import pytest

# ----------------------------
# Feature Tests: Configuration
# Env vars:
#   - Lists: comma-separated string of list names
#   - DefaultList: must be one of the names in Lists
# ----------------------------

@pytest.mark.skip(reason="Config validation not implemented yet")
def test_app_requires_valid_lists_and_defaultlist():
    """
    App should start ONLY if BOTH env vars are present and valid:
      - Lists is a non-empty, comma-separated list of names.
      - DefaultList is a non-empty string and is one of Lists.
    Otherwise, startup should fail with a clear error.
    """
    # TODO: Implement env validation checks (presence, non-empty, membership)
    pass


@pytest.mark.skip(reason="Tabs rendering and default selection not implemented yet")
def test_tabs_match_lists_and_default_selected_on_start():
    """
    Given valid Lists and DefaultList:
      - The visible tabs correspond exactly to the names from Lists (in order).
      - The tab corresponding to DefaultList is selected on startup.
    """
    # TODO: Verify tabs rendered from Lists and selected tab equals DefaultList
    pass


@pytest.mark.skip(reason="DefaultList membership check not implemented yet")
def test_defaultlist_must_be_in_lists_else_error():
    """
    If DefaultList is NOT one of the comma-separated entries in Lists:
      - The app should fail fast and report a helpful error.
    """
    # TODO: Start with mismatched DefaultList and assert a clear error is shown
    pass
    
    
    
# in dev always use develop and develop2
# in testing use test and test2
