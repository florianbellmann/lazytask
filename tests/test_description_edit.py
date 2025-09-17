import pytest


@pytest.mark.skip(reason="This test is for a feature that needs to be implemented.")
def test_edit_description_hotkey():
    """
    When the user presses the hotkey to edit the description of a selected task,
    a modal should appear with the current description, and submitting it
    should update the task.
    """
    # 1. Setup app with a list of tasks, one with a description.
    # 2. Select the task.
    # 3. Simulate pressing the 'edit description' hotkey.
    # 4. Check that the TextInputModal is on screen with the correct initial value.
    # 5. Simulate entering a new description and submitting.
    # 6. Check that the task's description has been updated.
    pass
