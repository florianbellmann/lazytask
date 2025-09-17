import pytest


@pytest.mark.skip(reason="This test is for a bug that needs to be fixed.")
def test_highlight_moves_correctly_after_completing_task_in_middle():
    """
    When a task in the middle of the list is completed, the highlight
    should move to the next task in the list (which takes the index
    of the completed task).
    """
    pass


@pytest.mark.skip(reason="This test is for a bug that needs to be fixed.")
def test_highlight_moves_correctly_after_completing_last_task():
    """
    When the last task in the list is completed, the highlight should
    move to the new last task in the list.
    """
    pass


@pytest.mark.skip(reason="This test is for a bug that needs to be fixed.")
def test_highlight_moves_correctly_after_completing_first_task():
    """
    When the first task in the list is completed, the highlight should
    move to the new first task in the list (the one that was second).
    """
    pass


@pytest.mark.skip(reason="This test is for a bug that needs to be fixed.")
def test_no_highlight_after_completing_only_task():
    """
    When the only task in the list is completed, the list becomes empty
    and there should be no highlighted task.
    """
    pass
