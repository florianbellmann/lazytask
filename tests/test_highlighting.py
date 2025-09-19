import pytest

import pytest

# ----------------------------
# Feature Tests: Highlighting & Selection (synchronized)
# ----------------------------


@pytest.mark.skip(reason="J/K navigation behavior not implemented yet")
def test_navigation_j_k_changes_highlight_and_selection():
    """
    Using 'J' moves the highlight/selection down one item; using 'K' moves it up one item.
    Both highlight and selection change together and remain in sync.
    """
    # TODO: Implement J/K navigation test
    pass


@pytest.mark.skip(reason="Highlight-selection sync enforcement not implemented yet")
def test_highlight_always_matches_selection():
    """
    The highlighted task is always the selected task; they never diverge.
    """
    # TODO: Implement invariant check to ensure no desync possible
    pass


@pytest.mark.skip(reason="Reset on list switch not implemented yet")
def test_selection_and_highlight_reset_to_first_on_list_switch():
    """
    When switching to another list OR to 'all lists' mode, set highlight/selection to the first item.
    If the destination list is empty, select and highlight nothing.
    """
    # TODO: Implement reset on list switch / all-list mode test
    pass


@pytest.mark.skip(reason="Completion selection rules not implemented yet")
def test_selection_after_completing_task_prefers_next_else_prev_else_none():
    """
    When completing the currently selected task:
      - Select/highlight the task below it, if any.
      - Otherwise select/highlight the previous task (above), if any.
      - If neither exists (list becomes empty), select/highlight nothing.
    """
    # TODO: Implement selection rules after completion
    pass


@pytest.mark.skip(reason="Post-add focus behavior not implemented yet")
def test_selection_and_highlight_move_to_new_task_after_adding():
    """
    After adding a new task, highlight/select the newly added task.
    """
    # TODO: Implement focus new task after add
    pass


@pytest.mark.skip(reason="Filtering selection rules not implemented yet")
def test_filtering_keeps_current_selection_unless_filtered_out_then_first_else_none():
    """
    While filtering:
      - Keep the current highlight/selection if the selected task still matches the filter.
      - If it no longer matches, select/highlight the first item in the filtered list.
      - If the filtered list is empty, select/highlight nothing.
    """
    # TODO: Implement selection rules during filtering
    pass


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
