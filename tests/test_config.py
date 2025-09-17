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
