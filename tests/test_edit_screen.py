import pytest


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
